import os
from datetime import datetime, timedelta, timezone

from planner.errors import PlanError
from planner.input import parse_trip
from planner.services.geocode import GeocodeError, geocode_place
from planner.services.geo import decode_polyline, simplify_line
from planner.services.recommend import rank_routes
from planner.services.risk import classify, summarize
from planner.services.router import RouteError, fetch_routes
from planner.services.sample import build_checkpoints, corridor_samples
from planner.services.weather import (
    WeatherError,
    corridor_hours,
    fetch_series,
    forecast_days_for,
    origin_clock,
    reading_at,
    score_corridor,
)

ROUTE_IDS = ("route-a", "route-b", "route-c")
ROUTE_NAMES = ("Route A", "Route B", "Route C")


def build_plan(body):
    query = parse_trip(body)
    origin_query = query.origin
    destination_query = query.destination
    load_lb = query.load_lb
    sample_miles = query.sample_miles

    api_key = os.environ.get("STADIA_API_KEY", "").strip()
    if not api_key:
        raise PlanError("STADIA_API_KEY is not set on the server.", 500)

    try:
        origin = geocode_place(origin_query, api_key)
        destination = geocode_place(destination_query, api_key)
    except GeocodeError as exc:
        raise PlanError(str(exc)) from exc

    if abs(origin["lat"] - destination["lat"]) < 0.02 and abs(origin["lon"] - destination["lon"]) < 0.02:
        raise PlanError("Origin and destination look like the same place.")

    try:
        timezone_name, offset_seconds = origin_clock(origin["lat"], origin["lon"])
    except WeatherError as exc:
        raise PlanError(str(exc), 502) from exc

    departure = _parse_departure(query.departure, offset_seconds)

    try:
        trips = fetch_routes(origin, destination, api_key)
    except RouteError as exc:
        raise PlanError(str(exc), 502) from exc

    routes = [_route_from_trip(index, trip, sample_miles) for index, trip in enumerate(trips)]
    points = corridor_samples(routes)
    hours = corridor_hours()
    etas = [
        departure + timedelta(seconds=checkpoint["seconds"])
        for route in routes
        for checkpoint in route["checkpoints"]
    ]
    forecast_days = forecast_days_for(etas + hours)

    try:
        series = fetch_series(
            [{"lat": item["lat"], "lon": item["lon"]} for route in routes for item in route["checkpoints"]]
            + points,
            forecast_days,
        )
    except WeatherError as exc:
        raise PlanError(str(exc), 502) from exc

    cursor = 0
    for route in routes:
        for checkpoint in route["checkpoints"]:
            eta = departure + timedelta(seconds=checkpoint["seconds"])
            wind, rain, snow = reading_at(series[cursor], eta)
            cursor += 1
            scored = classify(wind, rain, snow, load_lb)
            checkpoint["eta"] = eta.astimezone(timezone.utc).isoformat()
            checkpoint["wind_mph"] = _round(wind, 1)
            checkpoint["rain_in_hr"] = _round(rain, 2)
            checkpoint["snow_in_hr"] = _round(snow, 2)
            checkpoint["level"] = scored["level"]
            checkpoint["factors"] = scored["factors"]
            del checkpoint["seconds"]
        route["summary"] = summarize(route["checkpoints"])

    corridor_series = series[cursor:]
    ranked = rank_routes(routes)
    notes = []
    if len(ranked) < 3:
        word = "route" if len(ranked) == 1 else "routes"
        notes.append(f"The router returned {len(ranked)} {word} for this trip.")

    scored_miles = [
        checkpoint
        for route in ranked
        for checkpoint in route["checkpoints"]
        if checkpoint["stretch_miles"] > 0
    ]
    if scored_miles and all(checkpoint["level"] == "unknown" for checkpoint in scored_miles):
        notes.append("The forecast does not cover this departure, so risk miles were left blank.")

    for route in ranked:
        route["geometry"] = simplify_line(route["geometry"])
        del route["_points"]
        del route["_mile_at"]
        del route["_second_at"]

    return {
        "origin": {**origin, "timezone": timezone_name},
        "destination": destination,
        "departure": departure.astimezone(timezone.utc).isoformat(),
        "timezone": timezone_name,
        "load_weight_lb": load_lb,
        "sample_miles": sample_miles,
        "recommended_route_id": ranked[0]["id"] if ranked else None,
        "routes": ranked,
        "corridor": {
            "hours": [hour.isoformat() for hour in hours],
            "points": score_corridor(points, corridor_series, hours, load_lb),
        },
        "note": " ".join(notes) or None,
    }


def _route_from_trip(index, trip, sample_miles):
    leg = trip["legs"][0]
    points = decode_polyline(leg["shape"])
    checkpoints, mile_at, second_at = build_checkpoints(points, leg.get("maneuvers") or [], sample_miles)
    summary = trip.get("summary") or {}
    return {
        "id": ROUTE_IDS[index],
        "name": ROUTE_NAMES[index],
        "distance_miles": round(float(summary.get("length") or (mile_at[-1] if mile_at else 0)), 1),
        "duration_seconds": round(float(summary.get("time") or 0)),
        "has_toll": bool(summary.get("has_toll")),
        "has_highway": bool(summary.get("has_highway")),
        "geometry": [[lon, lat] for lat, lon in points],
        "checkpoints": checkpoints,
        "_points": points,
        "_mile_at": mile_at,
        "_second_at": second_at,
    }


def _parse_departure(value, offset_seconds):
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise PlanError("Departure time is not a valid date.")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone(timedelta(seconds=offset_seconds)))
    return parsed


def _round(value, places):
    if value is None:
        return None
    return round(float(value), places)
