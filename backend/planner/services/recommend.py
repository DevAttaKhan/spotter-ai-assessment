def rank_routes(routes):
    """Best route first.

    No-travel miles are compared before the four written rules. A stretch the
    driver cannot use is worse than a severe stretch. Ties then follow the
    brief: fewest severe miles, fewest high miles, lowest average, shortest time.
    """

    def sort_key(route):
        summary = route["summary"]
        average = summary["average_risk"]
        if average is None:
            average = 99
        return (
            summary["no_travel_miles"],
            summary["severe_miles"],
            summary["high_miles"],
            average,
            route["duration_seconds"],
        )

    ranked = sorted(routes, key=sort_key)
    for index, route in enumerate(ranked):
        route["rank"] = index + 1
        route["recommended"] = index == 0
    return ranked
