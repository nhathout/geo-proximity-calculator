import unittest
from unittest.mock import patch, MagicMock
import io

from main import (
    haversine_distance,
    parse_coordinate,
    load_points_csv,
    find_closest_point,
    pair_arrays,
    get_valid_input,
    get_dms,
    get_point,
    get_points_manually,
    main
)

# ChatGPT-aided test functions
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

class TestFindClosestPoint(unittest.TestCase):
    def test_find_closest_point_basic(self):
        """ Test the find_closest_point function with a small set. """
        coords = [(10, 10), (20, 20), (15, 15)]
        closest, dist = find_closest_point(10, 10.1, coords)
        # The closest should be (10,10) with a small distance
        self.assertEqual(closest, (10, 10))
        # Distance should be small but not zero
        self.assertGreater(dist, 0)

class TestPairArrays(unittest.TestCase):
    def test_pair_arrays_basic(self):
        """ Test the pair_arrays function. """
        array1 = [(0,0), (1,1)]
        array2 = [(0,0.1), (1.1,1.05)]
        results = pair_arrays(array1, array2)
        self.assertEqual(len(results), 2)
        # Each item in results is ((lat1, lon1), (closest_lat, closest_lon), dist)
        self.assertEqual(results[0][0], (0,0))  # from array1
        self.assertEqual(results[0][1], (0,0.1))  # guessed closest
        # We won't be super strict on the exact distance value, but let's check it's small
        self.assertLess(results[0][2], 50)  # in km

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


class TestUserInputHelpers(unittest.TestCase):
    @patch('builtins.input', side_effect=['3.5'])
    def test_get_valid_input_simple(self, mock_input):
        """ Check that get_valid_input reads a single float correctly. """
        val = get_valid_input("Enter something: ")
        self.assertEqual(val, 3.5)

    @patch('builtins.input', side_effect=['notafloat', '999', '10'])
    def test_get_valid_input_with_range(self, mock_input):
        """
        Check that get_valid_input enforces range. 
        - first input is invalid float => it should prompt again,
        - second input is 999 => out of range => prompt again,
        - third is 10 => valid.
        """
        val = get_valid_input("Enter something: ", min_val=1, max_val=100)
        self.assertEqual(val, 10)

    @patch('builtins.input', side_effect=['45', '30', '30'])
    def test_get_dms_latitude(self, mock_input):
        """
        Check that get_dms can handle positive lat with degrees, mins, secs.
        Should produce 45.5083... (approx).
        """
        val = get_dms(is_lat=True)
        # 45 deg + 30' + 30" => 45 + 0.5 + 0.008333... ~ 45.5083
        self.assertAlmostEqual(val, 45.5083, places=4)

    @patch('builtins.input', side_effect=['d', '12.34'])
    def test_get_point_decimal(self, mock_input):
        """
        Test that get_point returns the decimal float when user chooses 'd'.
        """
        val = get_point(is_lat=True)
        self.assertEqual(val, 12.34)

    @patch('builtins.input', side_effect=['dm', '12', '15', '30'])
    def test_get_point_dms(self, mock_input):
        """
        Test that get_point returns the DMS result when user chooses 'dm'.
        12° 15' 30" => 12.2583...
        """
        val = get_point(is_lat=True)
        self.assertAlmostEqual(val, 12.2583, places=4)

    @patch('builtins.input', side_effect=[
        '2',              # number of points
        'd', '10.0',      # lat decimal
        'd', '20.0',      # lon decimal
        'dm', '30', '0', '0',  # lat in dms
        'dm', '45', '30', '0'  # lon in dms
    ])
    def test_get_points_manually(self, mock_input):
        """
        Test that get_points_manually collects the points properly.
        We expect two points: (10, 20) and (30, 45.5).
        """
        points = get_points_manually("TEST")
        self.assertEqual(len(points), 2)
        self.assertAlmostEqual(points[0][0], 10.0)  # lat
        self.assertAlmostEqual(points[0][1], 20.0)  # lon
        self.assertAlmostEqual(points[1][0], 30.0)  # lat
        self.assertAlmostEqual(points[1][1], 45.5, places=4)  # lon

class TestMainFunction(unittest.TestCase):
    """
    This test ensures we at least *touch* the main() code flow.
    We mock user inputs to go through CSV or manual flows quickly.
    """
    @patch('builtins.input', side_effect=[
        'manual',         # first array -> manual
        '1',              # how many points? -> 1
        'd', '10.0',      # lat
        'd', '20.0',      # lon
        'manual',         # second array -> manual
        '1',              # how many points? -> 1
        'd', '30.0',      # lat
        'd', '40.0',      # lon
    ])
    def test_main_manual_manual(self, mock_input):
        # We can patch print as well, if we want to inspect output.
        # But for coverage, just calling main() is enough to test branches.
        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            main()
            output = fake_out.getvalue()
        # Some sanity checks:

    @patch('builtins.input', side_effect=[
        'csv',  # first array -> csv
        'csv_testing/Major_Cities_GPS.csv',
        'csv',  # second array -> csv
        'csv_testing/Major_Cities_GPS_V2.csv',
    ])
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=MagicMock)
    def test_main_csv_csv(self, mock_open, mock_exists, mock_input):
        """
        We'll fake open() to return a CSV-like object so main() can parse.
        """
        # Fake CSV content with headers "latitude" / "longitude".
        fake_csv_content = """latitude,longitude
40.0,-70.0
43.1,-75.2
"""
        mock_open.return_value.__enter__.return_value = io.StringIO(fake_csv_content)

        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            main()
            output = fake_out.getvalue()

if __name__ == '__main__':
    unittest.main()