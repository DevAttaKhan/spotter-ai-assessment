import logging

import requests

logger = logging.getLogger(__name__)

ROUTE_URL = "https://api.stadiamaps.com/route/v1"

# A common US tractor-trailer. Cargo weight is not sent here; it only affects risk.
TRUCK = {
    "height": 4.11,
    "width": 2.6,
    "length": 21.64,
}


class RouteError(Exception):
    pass


def fetch_routes(origin, destination, api_key):
    body = {
        "locations": [
            {"lat": origin["lat"], "lon": origin["lon"], "type": "break"},
            {"lat": destination["lat"], "lon": destination["lon"], "type": "break"},
        ],
        "costing": "truck",
        "costing_options": {"truck": TRUCK},
        "alternates": 2,
        "units": "miles",
    }
    try:
        response = requests.post(
            ROUTE_URL,
            json=body,
            headers={
                "Authorization": f"Stadia-Auth {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        logger.warning("Routing request failed: %s", exc)
        raise RouteError("Routing service did not respond.") from exc

    if response.status_code != 200:
        logger.warning("Routing status %s: %s", response.status_code, response.text[:400])
        raise RouteError("Routing service rejected the trip.")

    payload = response.json()
    trip = payload.get("trip") or {}
    if trip.get("status") not in (0, None):
        raise RouteError(trip.get("status_message") or "No route was found.")
    if not trip.get("legs"):
        raise RouteError("No route was found.")

    trips = [trip]
    for alternate in payload.get("alternates") or []:
        alternate_trip = alternate.get("trip")
        if alternate_trip and alternate_trip.get("legs"):
            trips.append(alternate_trip)
    return trips[:3]
