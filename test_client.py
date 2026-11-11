import unittest

from fortygraud_client import FortyGuardClient


class TestFortyGuardClient(unittest.TestCase):

    def test_payload_structure(self):

        payload = (
            FortyGuardClient.build_heatmap_payload()
        )

        self.assertIn("polygon_aoi", payload)
        self.assertIn("date_time", payload)
        self.assertIn("granularity", payload)

    def test_geojson_structure(self):

        payload = (
            FortyGuardClient.build_heatmap_payload()
        )

        polygon = payload["polygon_aoi"]

        self.assertEqual(
            polygon["type"],
            "FeatureCollection"
        )

        feature = polygon["features"][0]

        self.assertEqual(
            feature["geometry"]["type"],
            "Polygon"
        )

    def test_polygon_is_closed(self):

        payload = (
            FortyGuardClient.build_heatmap_payload()
        )

        coordinates = (
            payload["polygon_aoi"]
            ["features"][0]
            ["geometry"]["coordinates"][0]
        )

        self.assertEqual(
            coordinates[0],
            coordinates[-1]
        )

    def test_granularity(self):

        payload = (
            FortyGuardClient.build_heatmap_payload()
        )

        self.assertIn(
            payload["granularity"],
            [60, 80, 100]
        )

    def test_datetime_fields(self):

        payload = (
            FortyGuardClient.build_heatmap_payload()
        )

        date_time = payload["date_time"]

        self.assertIn("start_date", date_time)
        self.assertIn("start_time", date_time)
        self.assertIn("filter_type", date_time)


if __name__ == "__main__":
    unittest.main()