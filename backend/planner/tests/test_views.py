import json

from django.test import RequestFactory, SimpleTestCase

from planner.views import plan_view


class PlanViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_missing_fields_do_not_call_the_network(self):
        request = self.factory.post(
            "/api/plan/",
            data=json.dumps({}),
            content_type="application/json",
        )
        response = plan_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("origin", json.loads(response.content)["error"])

    def test_non_json_content_type_is_rejected(self):
        request = self.factory.post("/api/plan/", data="origin=Chicago", content_type="text/plain")
        response = plan_view(request)
        self.assertEqual(response.status_code, 415)

    def test_overlong_place_is_rejected_without_a_status_200(self):
        request = self.factory.post(
            "/api/plan/",
            data=json.dumps(
                {
                    "origin": "A" * 121,
                    "destination": "Denver, CO",
                    "departure": "2026-10-20T08:00",
                    "load_weight_lb": 35000,
                    "sample_miles": 25,
                }
            ),
            content_type="application/json",
        )
        response = plan_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("too long", json.loads(response.content)["error"])

    def test_bad_sample_spacing_is_rejected(self):
        request = self.factory.post(
            "/api/plan/",
            data=json.dumps(
                {
                    "origin": "Chicago, IL",
                    "destination": "Denver, CO",
                    "departure": "2026-10-20T08:00",
                    "load_weight_lb": 35000,
                    "sample_miles": 15,
                }
            ),
            content_type="application/json",
        )
        response = plan_view(request)
        self.assertEqual(response.status_code, 400)
