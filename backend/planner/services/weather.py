import logging
import time
from datetime import datetime, timedelta, timezone

import requests

from planner.services.metno import MetError, fetch_series as fetch_met_series
from planner.services.risk import SCORES, classify

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CHUNK_SIZE = 80
BUSY_STATUSES = {429, 502, 503}


class WeatherError(Exception):
    pass


def _busy_message(reason, status):
    text = (reason or "").lower()
    if status in BUSY_STATUSES or "overload" in text:
        return "The weather service is busy. Try again in a moment."
    if reason:
        return reason
    return "Weather service did not respond."


def _get_open_meteo(params, timeout=30):
    """GET Open-Meteo, retrying when the free service says it is overloaded."""
    last_error = WeatherError("Weather service did not respond.")
    for attempt in range(3):
        try:
            response = requests.get(
                OPEN_METEO_URL,
                params=params,
                headers={"User-Agent": "route-check/1.0"},
                timeout=timeout,
            )
        except requests.RequestException as exc:
            logger.warning("Open-Meteo request failed: %s", exc)
            last_error = WeatherError("Weather service did not respond.")
        else:
            reason = ""
            body = None
            try:
                body = response.json()
                if isinstance(body, dict):
                    reason = body.get("reason") or ""
            except ValueError:
                reason = response.text[:200]

            if response.status_code == 200 and not (isinstance(body, dict) and body.get("error")):
                return body

            logger.warning("Open-Meteo status %s: %s", response.status_code, reason[:300])
            last_error = WeatherError(_busy_message(reason, response.status_code))
            overloaded = response.status_code in BUSY_STATUSES or "overload" in reason.lower()
            if not overloaded:
                raise last_error

        if attempt < 2:
            time.sleep(0.6 * (attempt + 1))

    raise last_error


def origin_clock(lat, lon):
    """Timezone name and UTC offset at the origin."""
    try:
        body = _get_open_meteo(
            {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m",
                "timezone": "auto",
                "forecast_days": 1,
            },
            timeout=20,
        )
    except WeatherError as exc:
        logger.warning("Open-Meteo timezone failed (%s). Using the backup clock.", exc)
        return _timezone_from_backup(lat, lon)
    if "timezone" not in body or "utc_offset_seconds" not in body:
        return _timezone_from_backup(lat, lon)
    return body["timezone"], int(body["utc_offset_seconds"])


def _timezone_from_backup(lat, lon):
    try:
        response = requests.get(
            "https://timeapi.io/api/TimeZone/coordinate",
            params={"latitude": lat, "longitude": lon},
            headers={"User-Agent": "route-check/1.0"},
            timeout=15,
        )
    except requests.RequestException as exc:
        logger.warning("Backup timezone request failed: %s", exc)
        raise WeatherError("Could not read the timezone at the origin.") from exc
    if response.status_code != 200:
        raise WeatherError("Could not read the timezone at the origin.")
    body = response.json()
    name = body.get("timeZone")
    offset = (body.get("currentUtcOffset") or {}).get("seconds")
    if not name or offset is None:
        raise WeatherError("Could not read the timezone at the origin.")
    return name, int(offset)


def hour_key(moment):
    utc = moment.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    return utc.strftime("%Y-%m-%dT%H:%M")


def forecast_days_for(moments):
    if not moments:
        return 7
    latest = max(moments)
    days_ahead = (latest - datetime.now(timezone.utc)).total_seconds() / 86400
    if days_ahead <= 6:
        return 7
    return 16


def _rain_total(rain, showers):
    if rain is None and showers is None:
        return None
    return (rain or 0) + (showers or 0)


def _value_at(times, values, key):
    try:
        index = times.index(key)
    except ValueError:
        return None
    if index >= len(values):
        return None
    return values[index]


def fetch_series(points, forecast_days):
    """Hourly wind, rain, and snow for each point. Order matches `points`."""
    if not points:
        return []
    try:
        return _fetch_open_meteo(points, forecast_days)
    except WeatherError as exc:
        logger.warning("Open-Meteo forecast failed (%s). Using MET Norway.", exc)
        try:
            return fetch_met_series(points)
        except MetError as backup:
            raise WeatherError(
                "The weather service is busy, and the backup did not answer either."
            ) from backup


def _fetch_open_meteo(points, forecast_days):
    series = [None] * len(points)
    for start in range(0, len(points), CHUNK_SIZE):
        chunk = points[start : start + CHUNK_SIZE]
        payload = _fetch_chunk(chunk, forecast_days)
        locations = payload if isinstance(payload, list) else [payload]
        if len(locations) != len(chunk):
            raise WeatherError("Weather service returned an unexpected number of locations.")
        for offset, location in enumerate(locations):
            hourly = location.get("hourly") or {}
            times = hourly.get("time") or []
            rain = hourly.get("rain") or []
            showers = hourly.get("showers") or []
            series[start + offset] = {
                "times": times,
                "wind": hourly.get("wind_speed_10m") or [],
                "rain": [_rain_total(rain[i] if i < len(rain) else None, showers[i] if i < len(showers) else None) for i in range(len(times))],
                "snow": hourly.get("snowfall") or [],
            }
    return series


def _fetch_chunk(points, forecast_days):
    params = {
        "latitude": ",".join(f"{point['lat']:.4f}" for point in points),
        "longitude": ",".join(f"{point['lon']:.4f}" for point in points),
        "hourly": "wind_speed_10m,rain,showers,snowfall",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "UTC",
        "forecast_days": forecast_days,
    }
    return _get_open_meteo(params, timeout=30)


def reading_at(series, moment):
    if series is None:
        return None, None, None
    key = hour_key(moment)
    wind = _value_at(series["times"], series["wind"], key)
    rain = _value_at(series["times"], series["rain"], key)
    snow = _value_at(series["times"], series["snow"], key)
    return wind, rain, snow


def corridor_hours(count=49):
    start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    return [start + timedelta(hours=offset) for offset in range(count)]


def score_corridor(points, series_list, hours, load_lb):
    scored = []
    for point, series in zip(points, series_list):
        scores = []
        for moment in hours:
            wind, rain, snow = reading_at(series, moment)
            level = classify(wind, rain, snow, load_lb)["level"]
            scores.append(None if level == "unknown" else SCORES[level])
        scored.append(
            {
                "lat": round(point["lat"], 4),
                "lon": round(point["lon"], 4),
                "scores": scores,
            }
        )
    return scored
