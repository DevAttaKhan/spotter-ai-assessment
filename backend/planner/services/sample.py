from planner.services.geo import (
    bearing_degrees,
    destination_point,
    haversine_miles,
)


def shape_timeline(points, maneuvers):
    """Cumulative road miles and seconds at each shape point.

    Maneuver length and time are spread across that maneuver's shape span
    in proportion to the straight-line distance between points.
    """
    count = len(points)
    if count == 0:
        return [], []

    mile_at = [0.0] * count
    second_at = [0.0] * count

    for maneuver in maneuvers:
        start = max(0, min(int(maneuver["begin_shape_index"]), count - 1))
        end = max(start, min(int(maneuver.get("end_shape_index", start)), count - 1))
        length = float(maneuver.get("length") or 0)
        seconds = float(maneuver.get("time") or 0)

        if end == start:
            mile_at[end] = mile_at[start] + length
            second_at[end] = second_at[start] + seconds
            continue

        spans = [
            haversine_miles(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
            for i in range(start, end)
        ]
        geo = sum(spans)
        if geo == 0:
            mile_at[end] = mile_at[start] + length
            second_at[end] = second_at[start] + seconds
            continue

        walked_miles = 0.0
        walked_seconds = 0.0
        for offset, span in enumerate(spans):
            share = span / geo
            walked_miles += length * share
            walked_seconds += seconds * share
            mile_at[start + offset + 1] = mile_at[start] + walked_miles
            second_at[start + offset + 1] = second_at[start] + walked_seconds

    for index in range(1, count):
        if mile_at[index] < mile_at[index - 1]:
            mile_at[index] = mile_at[index - 1]
        if second_at[index] < second_at[index - 1]:
            second_at[index] = second_at[index - 1]

    return mile_at, second_at


def _locate(points, mile_at, second_at, target):
    if target <= 0:
        bearing = 0.0
        if len(points) > 1:
            bearing = bearing_degrees(points[0][0], points[0][1], points[1][0], points[1][1])
        return points[0][0], points[0][1], 0.0, bearing

    if target >= mile_at[-1]:
        bearing = 0.0
        if len(points) > 1:
            bearing = bearing_degrees(
                points[-2][0], points[-2][1], points[-1][0], points[-1][1]
            )
        return points[-1][0], points[-1][1], second_at[-1], bearing

    for index in range(1, len(points)):
        if mile_at[index] < target:
            continue
        span = mile_at[index] - mile_at[index - 1]
        fraction = 0 if span == 0 else (target - mile_at[index - 1]) / span
        lat = points[index - 1][0] + (points[index][0] - points[index - 1][0]) * fraction
        lon = points[index - 1][1] + (points[index][1] - points[index - 1][1]) * fraction
        seconds = second_at[index - 1] + (second_at[index] - second_at[index - 1]) * fraction
        bearing = bearing_degrees(
            points[index - 1][0], points[index - 1][1], points[index][0], points[index][1]
        )
        return lat, lon, seconds, bearing

    return points[-1][0], points[-1][1], second_at[-1], 0.0


def sample_targets(total_miles, interval):
    if total_miles <= 0:
        return [0.0]

    targets = [0.0]
    cursor = float(interval)
    while cursor < total_miles - 1:
        targets.append(cursor)
        cursor += interval

    if total_miles - targets[-1] < 1 and len(targets) > 1:
        targets[-1] = total_miles
    elif targets[-1] != total_miles:
        targets.append(total_miles)
    return targets


def build_checkpoints(points, maneuvers, interval):
    mile_at, second_at = shape_timeline(points, maneuvers)
    if not points:
        return [], mile_at, second_at

    total = mile_at[-1]
    previous = 0.0
    checkpoints = []
    for target in sample_targets(total, interval):
        lat, lon, seconds, _bearing = _locate(points, mile_at, second_at, target)
        checkpoints.append(
            {
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "mile": round(target, 1),
                "stretch_miles": round(0.0 if target == 0 else target - previous, 1),
                "seconds": seconds,
            }
        )
        previous = target
    return checkpoints, mile_at, second_at


def corridor_samples(routes):
    """Points along each route, plus a point to either side, for the heatmap."""
    longest = 0.0
    for route in routes:
        mile_at = route.get("_mile_at") or [0]
        longest = max(longest, mile_at[-1] if mile_at else 0)

    if longest < 400:
        spacing = 25
    elif longest < 900:
        spacing = 40
    else:
        spacing = 55
    side_miles = 16

    seen = set()
    chosen = []
    for route in routes:
        points = route["_points"]
        mile_at = route["_mile_at"]
        second_at = route["_second_at"]
        if len(points) < 2 or not mile_at:
            continue
        total = mile_at[-1]
        cursor = 0.0
        while cursor <= total + 0.01:
            lat, lon, _seconds, bearing = _locate(points, mile_at, second_at, min(cursor, total))
            offsets = (
                (lat, lon),
                destination_point(lat, lon, (bearing + 90) % 360, side_miles),
                destination_point(lat, lon, (bearing - 90) % 360, side_miles),
            )
            for olat, olon in offsets:
                key = (round(olat, 2), round(olon, 2))
                if key in seen:
                    continue
                seen.add(key)
                chosen.append({"lat": olat, "lon": olon})
            cursor += spacing

    if len(chosen) > 240:
        step = (len(chosen) - 1) / 239
        chosen = [chosen[round(i * step)] for i in range(240)]
    return chosen
