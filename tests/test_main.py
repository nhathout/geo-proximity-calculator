import unittest
from unittest.mock import patch
from main import (
    haversine_distance,
    parse_coordinate,
    load_points_csv
)

# ChatGPT-aided test cases
class TestGeoCalculations(unittest.TestCase):
    def test_haversine_distance(self):
        """
        Simple distance check: London (51.5074, -0.1278) to Paris (48.8566, 2.3522)
        is roughly 343 km. We allow ±5 km for rounding.
        """
        dist = haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
        self.assertAlmostEqual(dist, 343, delta=5)

    def test_parse_coordinate(self):
        """
        Check that parse_coordinate handles degrees + directions,
        plain floats, and invalid input.
        """
        self.assertEqual(parse_coordinate("40.7128° N"), 40.7128)
        self.assertEqual(parse_coordinate("33.8688° S"), -33.8688)
        self.assertEqual(parse_coordinate("151.2093"), 151.2093)
        self.assertIsNone(parse_coordinate("invalid"))

class TestCSVHandling(unittest.TestCase):
    def test_load_points_csv_major_cities(self):
        """
        Test loading the first CSV: csv_testing/Major_Cities_GPS.csv
        We patch builtins.input so that load_points_csv() doesn't prompt.
        """
        with patch('builtins.input', return_value='csv_testing/Major_Cities_GPS.csv'):
            results = load_points_csv("test")
            # check we got at least one row
            self.assertGreater(len(results), 0)

    def test_load_points_csv_major_cities_v2(self):
        """
        Test loading the second CSV: csv_testing/Major_Cities_GPS_V2.csv
        """
        with patch('builtins.input', return_value='csv_testing/Major_Cities_GPS_V2.csv'):
            results = load_points_csv("test")
            self.assertGreater(len(results), 0)

if __name__ == '__main__':
    unittest.main()