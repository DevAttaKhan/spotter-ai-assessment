import logging
import time
from concurrent.futures import ThreadPoolExecutor

import requests

logger = logging.getLogger(__name__)

MET_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
USER_AGENT = "route-check/1.0 (https://github.com/DevAttaKhan/spotter-ai-assessment)"
MPH_PER_MPS = 2.2369362920544
INCHES_PER_MM = 1 / 25.4


class MetError(Exception):
    pass


def split_precip(millimeters, symbol):
    """MET Norway gives one precipitation total. The symbol says rain or snow."""
    inches = 0.0 if millimeters is None else float(millimeters) * INCHES_PER_MM
    code = (symbol or "").lower()
    if "snow" in code or "sleet" in code:
        return 0.0, inches
    return inches, 0.0


def fetch_series(points):
    """Hourly wind (mph), rain, and snow (in/hr) for each point. Order matches `points`."""
    if not points:
        return []
    workers = min(4, len(points))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_series_for_point, points))


def _series_for_point(point):
    params = {"lat": f"{point['lat']:.4f}", "lon": f"{point['lon']:.4f}"}
    last_error = MetError("Backup weather service did not respond.")
    for attempt in range(2):
        try:
            response = requests.get(
                MET_URL,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=20,
            )
        except requests.RequestException as exc:
            logger.warning("MET Norway request failed: %s", exc)
            last_error = MetError("Backup weather service did not respond.")
        else:
            if response.status_code == 200:
                return _series_from_body(response.json())
            logger.warning("MET Norway status %s: %s", response.status_code, response.text[:200])
            last_error = MetError("Backup weather service did not respond.")
            if response.status_code not in (429, 502, 503):
                raise last_error
        if attempt == 0:
            time.sleep(1)
    raise last_error


def _series_from_body(body):
    times = []
    wind = []
    rain = []
    snow = []
    for entry in body.get("properties", {}).get("timeseries") or []:
        data = entry.get("data") or {}
        instant = (data.get("instant") or {}).get("details") or {}
        hour = data.get("next_1_hours") or {}
        details = hour.get("details") or {}
        symbol = (hour.get("summary") or {}).get("symbol_code") or ""
        rain_in, snow_in = split_precip(details.get("precipitation_amount"), symbol)
        speed = instant.get("wind_speed")
        times.append(str(entry.get("time") or "")[:16])
        wind.append(None if speed is None else round(float(speed) * MPH_PER_MPS, 1))
        rain.append(round(rain_in, 2))
        snow.append(round(snow_in, 2))
    return {"times": times, "wind": wind, "rain": rain, "snow": snow}
