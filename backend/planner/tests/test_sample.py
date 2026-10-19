from django.test import SimpleTestCase

from planner.services.geo import decode_polyline, destination_point, haversine_miles
from planner.services.sample import build_checkpoints, sample_targets


class PolylineTests(SimpleTestCase):
    def test_google_precision_five_fixture(self):
        encoded = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
        points = decode_polyline(encoded, precision=5)
        self.assertEqual(len(points), 3)
        self.assertAlmostEqual(points[0][0], 38.5, places=3)
        self.assertAlmostEqual(points[0][1], -120.2, places=3)
        self.assertAlmostEqual(points[2][0], 43.252, places=3)
        self.assertAlmostEqual(points[2][1], -126.453, places=3)


class SampleTargetTests(SimpleTestCase):
    def test_includes_a_short_final_stretch(self):
        self.assertEqual(sample_targets(80, 25), [0.0, 25.0, 50.0, 75.0, 80.0])

    def test_short_trip_is_one_stretch(self):
        self.assertEqual(sample_targets(30, 50), [0.0, 30.0])

    def test_exact_multiple(self):
        self.assertEqual(sample_targets(100, 25), [0.0, 25.0, 50.0, 75.0, 100.0])


class CheckpointTests(SimpleTestCase):
    def test_eta_follows_maneuver_time_not_a_single_speed(self):
        points = [(40.0, -90.0), (41.0, -90.0), (42.0, -90.0)]
        maneuvers = [
            {"begin_shape_index": 0, "end_shape_index": 2, "length": 100, "time": 7200},
        ]
        checkpoints, mile_at, _seconds = build_checkpoints(points, maneuvers, 50)
        self.assertAlmostEqual(mile_at[-1], 100, places=5)
        self.assertEqual([item["mile"] for item in checkpoints], [0.0, 50.0, 100.0])
        self.assertEqual([item["stretch_miles"] for item in checkpoints], [0.0, 50.0, 50.0])
        self.assertAlmostEqual(checkpoints[1]["seconds"], 3600, places=3)
        self.assertAlmostEqual(checkpoints[2]["seconds"], 7200, places=3)
        self.assertAlmostEqual(checkpoints[1]["lat"], 41.0, places=3)


class OffsetTests(SimpleTestCase):
    def test_offset_is_about_the_requested_distance(self):
        lat, lon = destination_point(41.8, -87.6, 90, 16)
        self.assertAlmostEqual(haversine_miles(41.8, -87.6, lat, lon), 16, delta=0.2)
