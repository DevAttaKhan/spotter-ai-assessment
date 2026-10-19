from planner.errors import PlanError

MAX_PLACE_LENGTH = 120
SAMPLE_MILES = (10, 25, 50)
MAX_LOAD_LB = 100_000


class TripQuery:
    """The fields a plan is allowed to depend on. Nothing else from the body is read."""

    def __init__(self, origin, destination, departure, load_lb, sample_miles):
        self.origin = origin
        self.destination = destination
        self.departure = departure
        self.load_lb = load_lb
        self.sample_miles = sample_miles


def parse_trip(body):
    if not isinstance(body, dict):
        raise PlanError("Request body must be a JSON object.")

    origin = _place(body.get("origin"), "origin")
    destination = _place(body.get("destination"), "destination")
    if not origin or not destination:
        raise PlanError("Enter an origin and a destination.")

    departure = _text(body.get("departure"))
    if not departure:
        raise PlanError("Enter a departure date and time.")

    return TripQuery(
        origin=origin,
        destination=destination,
        departure=departure,
        load_lb=_load(body.get("load_weight_lb")),
        sample_miles=_sample(body.get("sample_miles")),
    )


def _place(value, label):
    text = _text(value)
    if not text:
        return ""
    if len(text) > MAX_PLACE_LENGTH:
        raise PlanError(f"The {label} is too long. Use a city and state.")
    if any(ord(char) < 32 for char in text):
        raise PlanError(f"The {label} has characters this search cannot use.")
    return text


def _text(value):
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def _load(value):
    try:
        load = float(value)
    except (TypeError, ValueError):
        raise PlanError("Enter a load weight in pounds.")
    if load <= 0 or load > MAX_LOAD_LB:
        raise PlanError("Load weight needs to be between 1 and 100,000 lb.")
    return load


def _sample(value):
    try:
        miles = int(value)
    except (TypeError, ValueError):
        raise PlanError("Choose a sample spacing of 10, 25, or 50 miles.")
    if miles not in SAMPLE_MILES:
        raise PlanError("Choose a sample spacing of 10, 25, or 50 miles.")
    return miles
