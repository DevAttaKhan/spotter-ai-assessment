import math

EARTH_MILES = 3958.7613


def haversine_miles(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_MILES * math.asin(math.sqrt(a))


def bearing_degrees(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def destination_point(lat, lon, bearing, miles):
    delta = miles / EARTH_MILES
    theta = math.radians(bearing)
    phi1 = math.radians(lat)
    lambda1 = math.radians(lon)
    phi2 = math.asin(
        math.sin(phi1) * math.cos(delta) + math.cos(phi1) * math.sin(delta) * math.cos(theta)
    )
    lambda2 = lambda1 + math.atan2(
        math.sin(theta) * math.sin(delta) * math.cos(phi1),
        math.cos(delta) - math.sin(phi1) * math.sin(phi2),
    )
    wrapped = (math.degrees(lambda2) + 540) % 360 - 180
    return math.degrees(phi2), wrapped


def decode_polyline(encoded, precision=6):
    """Decode a Valhalla polyline (precision 6) into (lat, lon) pairs."""
    factor = 10 ** precision
    points = []
    index = 0
    lat = 0
    lon = 0
    length = len(encoded)

    while index < length:
        for axis in range(2):
            shift = 0
            result = 0
            while True:
                chunk = ord(encoded[index]) - 63
                index += 1
                result |= (chunk & 0x1F) << shift
                shift += 5
                if chunk < 0x20:
                    break
            delta = ~(result >> 1) if result & 1 else result >> 1
            if axis == 0:
                lat += delta
            else:
                lon += delta
        points.append((lat / factor, lon / factor))

    return points


def simplify_line(coordinates, limit=2000):
    """Keep [lon, lat] pairs under `limit` so the map payload stays small."""
    if len(coordinates) <= limit:
        return coordinates
    step = (len(coordinates) - 1) / (limit - 1)
    kept = [coordinates[round(i * step)] for i in range(limit - 1)]
    kept.append(coordinates[-1])
    return kept
