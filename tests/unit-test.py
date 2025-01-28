import unittest
from unittest.mock import patch
import os
from main import (
    haversine_distance,
    parse_coordinate,
    load_points_csv,
    get_valid_input
)

class TestGeoCalculations(unittest.TestCase):
    def test_haversine_distance(self):
        # Test known distance (London to Paris ≈ 343 km)
        dist = haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
        self.assertAlmostEqual(dist, 343, delta=5)

    def test_parse_coordinate(self):
        self.assertEqual(parse_coordinate("40.7128° N"), 40.7128)
        self.assertEqual(parse_coordinate("33.8688° S"), -33.8688)
        self.assertEqual(parse_coordinate("151.2093"), 151.2093)
        self.assertIsNone(parse_coordinate("invalid"))

class TestCSVHandling(unittest.TestCase):
    def setUp(self):
        self.test_csv = "test_coords.csv"
        with open(self.test_csv, "w") as f:
            f.write("Latitude,Longitude\n40.7128 N,74.0060 W\n48.8566,2.3522")

    def test_load_points_csv(self):
        results = load_points_csv("test")
        self.assertEqual(results, [(40.7128, -74.006), (48.8566, 2.3522)])

    def tearDown(self):
        os.remove(self.test_csv)

class TestCLI(unittest.TestCase):
    @patch('builtins.input', side_effect=['csv', 'test.csv'])
    def test_csv_input_flow(self, mock_input):
        with patch('your_module.load_points_csv') as mock_load:
            mock_load.return_value = [(40.7128, -74.006)]
            result = load_points_csv("test")
            self.assertTrue(mock_load.called)

if __name__ == '__main__':
    unittest.main()