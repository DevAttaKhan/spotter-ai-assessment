from django.test import SimpleTestCase

from planner.services.risk import classify, rain_level, snow_level, summarize, wind_level


class WindBandTests(SimpleTestCase):
    def test_table_boundaries(self):
        self.assertEqual(wind_level(24.9, 10000), "low")
        self.assertEqual(wind_level(25, 10000), "moderate")
        self.assertEqual(wind_level(34, 10000), "moderate")
        self.assertEqual(wind_level(35, 10000), "high")
        self.assertEqual(wind_level(44, 10000), "high")
        self.assertEqual(wind_level(45, 10000), "severe")
        self.assertEqual(wind_level(54, 10000), "severe")
        self.assertEqual(wind_level(55, 10000), "no_travel")

    def test_load_does_not_change_bands_below_the_cutoffs(self):
        self.assertEqual(wind_level(34, 80000), "moderate")
        self.assertEqual(wind_level(44, 40000), "high")
        self.assertEqual(wind_level(45, 30000), "severe")
        self.assertEqual(wind_level(54, 30000), "severe")

    def test_heavy_load_upgrades_wind(self):
        self.assertEqual(wind_level(35, 40001), "severe")
        self.assertEqual(wind_level(44, 40001), "severe")
        self.assertEqual(wind_level(45, 30001), "no_travel")
        self.assertEqual(wind_level(54, 30001), "no_travel")
        self.assertEqual(wind_level(55, 1), "no_travel")


class RainAndSnowTests(SimpleTestCase):
    def test_rain_boundaries(self):
        self.assertEqual(rain_level(0.09), "low")
        self.assertEqual(rain_level(0.10), "moderate")
        self.assertEqual(rain_level(0.24), "moderate")
        self.assertEqual(rain_level(0.25), "high")
        self.assertEqual(rain_level(0.49), "high")
        self.assertEqual(rain_level(0.50), "severe")
        self.assertEqual(rain_level(1.00), "severe")
        self.assertEqual(rain_level(1.01), "no_travel")

    def test_snow_boundaries(self):
        self.assertEqual(snow_level(0.49), "low")
        self.assertEqual(snow_level(0.5), "moderate")
        self.assertEqual(snow_level(0.99), "moderate")
        self.assertEqual(snow_level(1.0), "high")
        self.assertEqual(snow_level(1.99), "high")
        self.assertEqual(snow_level(2.0), "severe")
        self.assertEqual(snow_level(3.0), "severe")
        self.assertEqual(snow_level(3.01), "no_travel")


class ClassifyTests(SimpleTestCase):
    def test_worst_condition_wins(self):
        scored = classify(10, 0.6, 0.1, 20000)
        self.assertEqual(scored["level"], "severe")
        self.assertEqual(scored["factors"], ["rain"])

    def test_missing_weather_is_unknown(self):
        scored = classify(None, None, None, 20000)
        self.assertEqual(scored["level"], "unknown")
        self.assertEqual(scored["factors"], [])


class SummarizeTests(SimpleTestCase):
    def test_mile_weighted_average(self):
        checkpoints = [
            {"stretch_miles": 0, "level": "severe"},
            {"stretch_miles": 10, "level": "severe"},
            {"stretch_miles": 30, "level": "low"},
        ]
        summary = summarize(checkpoints)
        self.assertEqual(summary["severe_miles"], 10)
        self.assertEqual(summary["low_miles"], 30)
        self.assertEqual(summary["average_risk"], 1.75)
        self.assertEqual(summary["no_travel_miles"], 0)

    def test_unknown_miles_are_left_out(self):
        summary = summarize([{"stretch_miles": 20, "level": "unknown"}])
        self.assertIsNone(summary["average_risk"])
        self.assertEqual(summary["severe_miles"], 0)
