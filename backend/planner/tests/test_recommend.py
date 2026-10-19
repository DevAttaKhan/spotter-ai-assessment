from django.test import SimpleTestCase

from planner.services.recommend import rank_routes


def _route(name, no_travel, severe, high, average, seconds):
    return {
        "name": name,
        "duration_seconds": seconds,
        "summary": {
            "no_travel_miles": no_travel,
            "severe_miles": severe,
            "high_miles": high,
            "average_risk": average,
        },
    }


class RankTests(SimpleTestCase):
    def test_no_travel_miles_outrank_a_shorter_severe_route(self):
        blocked = _route("blocked", 10, 0, 0, 5, 1000)
        severe = _route("severe", 0, 80, 0, 4, 5000)
        ranked = rank_routes([blocked, severe])
        self.assertEqual(ranked[0]["name"], "severe")
        self.assertTrue(ranked[0]["recommended"])
        self.assertEqual(ranked[1]["rank"], 2)

    def test_fewer_severe_miles_wins(self):
        worse = _route("worse", 0, 40, 0, 2, 1000)
        better = _route("better", 0, 10, 90, 3, 9000)
        ranked = rank_routes([worse, better])
        self.assertEqual(ranked[0]["name"], "better")

    def test_fewer_high_miles_breaks_a_severe_tie(self):
        more_high = _route("more", 0, 10, 50, 1, 1000)
        less_high = _route("less", 0, 10, 20, 3, 9000)
        ranked = rank_routes([more_high, less_high])
        self.assertEqual(ranked[0]["name"], "less")

    def test_lower_average_breaks_the_next_tie(self):
        higher = _route("higher", 0, 10, 10, 2.4, 1000)
        lower = _route("lower", 0, 10, 10, 1.8, 9000)
        ranked = rank_routes([higher, lower])
        self.assertEqual(ranked[0]["name"], "lower")

    def test_shorter_time_is_the_last_tie_break(self):
        slow = _route("slow", 0, 10, 10, 1.5, 8000)
        fast = _route("fast", 0, 10, 10, 1.5, 4000)
        ranked = rank_routes([slow, fast])
        self.assertEqual(ranked[0]["name"], "fast")

    def test_missing_average_sorts_after_a_scored_route(self):
        blank = _route("blank", 0, 0, 0, None, 1000)
        scored = _route("scored", 0, 0, 0, 2, 9000)
        ranked = rank_routes([blank, scored])
        self.assertEqual(ranked[0]["name"], "scored")
