import logging

import requests

logger = logging.getLogger(__name__)

SEARCH_URL = "https://api.stadiamaps.com/geocoding/v1/search"


class GeocodeError(Exception):
    pass


def geocode_place(query, api_key):
    try:
        response = requests.get(
            SEARCH_URL,
            params={"text": query, "size": 1},
            headers={"Authorization": f"Stadia-Auth {api_key}"},
            timeout=20,
        )
    except requests.RequestException as exc:
        logger.warning("Geocoder request failed: %s", exc)
        raise GeocodeError("Geocoder did not respond.") from exc

    if response.status_code != 200:
        logger.warning("Geocoder status %s: %s", response.status_code, response.text[:300])
        raise GeocodeError("Geocoder rejected the lookup.")

    features = response.json().get("features") or []
    if not features:
        raise GeocodeError(f'No match for "{query}". Try a city and state.')

    feature = features[0]
    lon, lat = feature["geometry"]["coordinates"]
    label = feature.get("properties", {}).get("label") or query
    return {"label": label, "lat": lat, "lon": lon}
