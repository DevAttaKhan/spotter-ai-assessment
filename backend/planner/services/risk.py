# Scores are only used for the average. The sort uses mile totals, not this scale.
SCORES = {
    "low": 1,
    "moderate": 2,
    "high": 3,
    "severe": 4,
    "no_travel": 5,
}


def wind_level(mph, load_lb):
    # The printed table uses whole-number bands. 25, 35, 45, and 55 belong to
    # the higher band. 34 is still moderate; 35 is high.
    if mph >= 55:
        return "no_travel"
    if mph >= 45:
        if load_lb > 30000:
            return "no_travel"
        return "severe"
    if mph >= 35:
        if load_lb > 40000:
            return "severe"
        return "high"
    if mph >= 25:
        return "moderate"
    return "low"


def rain_level(inches_per_hour):
    # 0.25 and 0.50 sit in two printed buckets. The worse bucket wins.
    # 1.00 is still severe; no travel starts above 1.00.
    if inches_per_hour > 1:
        return "no_travel"
    if inches_per_hour >= 0.5:
        return "severe"
    if inches_per_hour >= 0.25:
        return "high"
    if inches_per_hour >= 0.1:
        return "moderate"
    return "low"


def snow_level(inches_per_hour):
    # 1.0, 2.0, and 3.0 sit in two printed buckets. The worse bucket wins.
    # 3.0 is still severe; no travel starts above 3.0.
    if inches_per_hour > 3:
        return "no_travel"
    if inches_per_hour >= 2:
        return "severe"
    if inches_per_hour >= 1:
        return "high"
    if inches_per_hour >= 0.5:
        return "moderate"
    return "low"


def _worse(left, right):
    if SCORES[left] >= SCORES[right]:
        return left
    return right


def classify(wind_mph, rain_in_hr, snow_in_hr, load_lb):
    parts = []
    if wind_mph is not None:
        parts.append(("wind", wind_level(wind_mph, load_lb)))
    if rain_in_hr is not None:
        parts.append(("rain", rain_level(rain_in_hr)))
    if snow_in_hr is not None:
        parts.append(("snow", snow_level(snow_in_hr)))

    if not parts:
        return {"level": "unknown", "factors": []}

    winning = parts[0][1]
    for _, level in parts[1:]:
        winning = _worse(winning, level)

    factors = []
    if winning != "low":
        factors = [name for name, level in parts if level == winning]

    return {"level": winning, "factors": factors}


def summarize(checkpoints):
    totals = {name: 0.0 for name in SCORES}
    weighted = 0.0
    known_miles = 0.0

    for checkpoint in checkpoints:
        miles = float(checkpoint["stretch_miles"])
        level = checkpoint["level"]
        if miles <= 0 or level not in totals:
            continue
        totals[level] += miles
        weighted += SCORES[level] * miles
        known_miles += miles

    average = round(weighted / known_miles, 2) if known_miles else None
    return {
        "low_miles": round(totals["low"], 1),
        "moderate_miles": round(totals["moderate"], 1),
        "high_miles": round(totals["high"], 1),
        "severe_miles": round(totals["severe"], 1),
        "no_travel_miles": round(totals["no_travel"], 1),
        "average_risk": average,
    }
