from unittest.mock import patch

from django.test import SimpleTestCase

from planner.services.metno import split_precip
from planner.services.weather import WeatherError, fetch_series, origin_clock


class MetSplitTests(SimpleTestCase):
    def test_rain_symbol_keeps_the_total_as_rain(self):
        rain, snow = split_precip(25.4, "heavyrain")
        self.assertAlmostEqual(rain, 1.0)
        self.assertEqual(snow, 0.0)

    def test_snow_symbol_keeps_the_total_as_snow(self):
        rain, snow = split_precip(12.7, "snow")
        self.assertEqual(rain, 0.0)
        self.assertAlmostEqual(snow, 0.5)

    def test_sleet_counts_as_snow(self):
        rain, snow = split_precip(2.54, "sleet")
        self.assertEqual(rain, 0.0)
        self.assertAlmostEqual(snow, 0.1)

    def test_missing_amount_is_zero(self):
        self.assertEqual(split_precip(None, "clearsky_day"), (0.0, 0.0))


class WeatherFallbackTests(SimpleTestCase):
    def test_forecast_uses_met_when_open_meteo_is_busy(self):
        points = [{"lat": 41.8, "lon": -87.6}]
        met = [{"times": ["2026-10-20T16:00"], "wind": [10], "rain": [0], "snow": [0]}]
        with patch(
            "planner.services.weather._fetch_open_meteo",
            side_effect=WeatherError("The weather service is busy. Try again in a moment."),
        ):
            with patch("planner.services.weather.fetch_met_series", return_value=met) as backup:
                result = fetch_series(points, 7)
        backup.assert_called_once_with(points)
        self.assertEqual(result, met)

    def test_origin_clock_uses_the_backup_when_open_meteo_is_busy(self):
        response = type("Response", (), {})()
        response.status_code = 200
        response.json = lambda: {"timeZone": "America/Chicago", "currentUtcOffset": {"seconds": -18000}}
        with patch(
            "planner.services.weather._get_open_meteo",
            side_effect=WeatherError("The weather service is busy. Try again in a moment."),
        ):
            with patch("planner.services.weather.requests.get", return_value=response):
                name, offset = origin_clock(41.88, -87.63)
        self.assertEqual(name, "America/Chicago")
        self.assertEqual(offset, -18000)
