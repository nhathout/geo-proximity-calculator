import math
import csv
import os
import re
import logging
import tracemalloc
import cProfile
import pstats

# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # can change to NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL

# to handle console messages
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
ch.setFormatter(formatter)

# dont duplicate if logger is re-imported
if not logger.handlers:
    logger.addHandler(ch)

# function to calculate Haversine distance between to geo locations
def haversine_distance(lat1, lon1, lat2, lon2):
    logger.debug(f"Calculating Haversine distance between ({lat1}, {lon1}) and ({lat2}, {lon2})")

    R = 6371e3  # Earth radius in meters
    
    # Convert lat/long from degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in meters
    distance = R * c

    # Distance in km from m
    distance_km = distance / 1000
    logger.debug(f"Distance (km): {distance_km:.4f}")
    return distance_km

# function to find closest point in an array of points to a reference point
def find_closest_point(temp_lat, temp_lon, array_of_coords):
    logger.debug(f"Finding closest point to ({temp_lat}, {temp_lon}) among {len(array_of_coords)} points.")

    min_distance = None
    closest_point = None
    
    for (lat, lon) in array_of_coords:
        dist = haversine_distance(temp_lat, temp_lon, lat, lon)
        if min_distance is None or dist < min_distance:
            min_distance = dist
            closest_point = (lat, lon)

    logger.debug(f"Closest point is {closest_point} at distance {min_distance:.4f} km.")
    return closest_point, min_distance

# function that, for each (lat, lon) in array1, it finds the closest point in array2
# returns: [((lat1, lon1), closestLat, closestLon), distanceInKm), ( same for point 2 )]
def pair_arrays(array1, array2):
    logger.info(f"Pairing {len(array1)} points from array1 with their closest in array2 ({len(array2)} points).")

    matched_pairs = []

    for (lat1, lon1) in array1:
        (closest_lat, closest_lon), dist_km = find_closest_point(lat1, lon1, array2)
        matched_pairs.append(((lat1, lon1), (closest_lat, closest_lon), dist_km))

    return matched_pairs

# function to continuously ask user for a float until a float is entered.
# if min_val and/or max_val inputted, also checks that value is in specified range.
def get_valid_input(prompt, min_val=None, max_val=None):
    while True:
        user_input = input(prompt).strip()
        logger.debug(f"User input received: {user_input}")

        try:
            val = float(user_input)
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                logger.warning(f"Value {val} out of range: must be between {min_val} and {max_val}.")

                print(f"Error: value {val} out of range. Must be between {min_val} and {max_val}.")
                continue
            return val
        except ValueError:
            logger.warning(f"Invalid float input: '{user_input}'")

            print(f"Error: '{user_input}' is not a valid float. Please try again.")

# function to prompt user for degrees, mins, secs, for either lat or lon
# returns decimal degrees
def get_dms(is_lat=True):
    # for latitude, range is -90 to 90 degrees; for longitude, range is -180 to 180 degrees
    label = "latitude" if is_lat else "longitude"
    
    d_min, d_max = (-90, 90) if is_lat else (-180, 180)
    d = get_valid_input(f"Enter degrees for {label} (between {d_min} and {d_max}): ", d_min, d_max)
    
    m = get_valid_input(f"Enter minutes for {label} (0 to 59): ", 0, 59)
    s = get_valid_input(f"Enter seconds for {label} (0 to 59): ", 0, 59)
    
    # convert
    sign = 1 if d >= 0 else -1
    d_abs = abs(d)
    decimal_degrees = sign * (d_abs + m/60 + s/3600)
    logger.debug(f"Computed DMS -> {decimal_degrees} ({label})")
    return decimal_degrees

def get_point(is_lat=True):
    label = "latitude" if is_lat else "longitude"

    while True:
        choice = input(f"Do you want to enter {label} in decimal (d) or Degrees Minutes Seconds (dm)? [d/dm]: ").strip().lower()
        logger.debug(f"User chose format {choice} for {label}")
        if choice == "d":
            d_min, d_max = (-90, 90) if is_lat else (-180, 180)
            return get_valid_input(f"Enter {label} in decimal degrees: ", d_min, d_max)
        elif choice == "dm":
            return get_dms(is_lat=is_lat)
        else:
            logger.warning(f"Invalid choice for {label}: {choice}")
            print("Invalid choice. Type 'd' or 'dm'.")

# function to constantly prompt users for lat/lon (decimal or DMS)
def get_points_manually(label):
    num_points = int(get_valid_input(f"How many geo locations are in your {label} array? ", min_val=1))
    arr = []
    for i in range(num_points):
        logger.info(f"{label} array: Enter coordinates for point #{i+1}.")

        print(f"\n{label} array: Enter coordinates for point #{i+1}.")
        lat = get_point(is_lat=True)
        lon = get_point(is_lat=False)
        arr.append((lat, lon))
    logger.info(f"Collected {len(arr)} points for {label} array.")
    return arr

# function that parses a CSV input (like "33.8688° S" or "40.7128° N") into a float
def parse_coordinate(value):
    logger.debug(f"Parsing coordinate: {value}")

    cleaned = re.sub(r'[^0-9a-zA-Z\.\-]', '', value)
    
    # get direction (last letter if present)
    direction = None
    if len(cleaned) > 0 and cleaned[-1].upper() in ['N', 'S', 'E', 'W']:
        direction = cleaned[-1].upper()
        numeric_part = cleaned[:-1]
    else:
        numeric_part = cleaned
    
    try:
        coord = float(numeric_part)
    except ValueError:
        logger.warning(f"Could not parse numeric part from: {value}")

        return None
    
    if direction in ['S', 'W']:
        coord = -abs(coord)
    elif direction in ['N', 'E']:
        coord = abs(coord)
    
    return coord

# function to prompt user for CSV file path, try to read lat/lon columns and return a list of (lat, lon) tuples
def load_points_csv(label):
    filepath = input(f"Enter the path to the CSV file for your {label} array: ").strip()
    logger.info(f"Attempting to load CSV from: {filepath}")

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")

        print(f"Error: File '{filepath}' not found.")
        return []

    coords = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        possible_lat_cols = ["latitude", "lat", "Latitude"]
        possible_lon_cols = ["longitude", "lon", "Longitude"]
        
        for row in reader:
            lat, lon = None, None
            
            # find latitude
            for col in possible_lat_cols:
                if col in row and row[col].strip():
                    parsed = parse_coordinate(row[col])
                    if parsed is not None:
                        lat = parsed
                        break
            
            # find longitude
            for col in possible_lon_cols:
                if col in row and row[col].strip():
                    parsed = parse_coordinate(row[col])
                    if parsed is not None:
                        lon = parsed
                        break
            
            if lat is not None and lon is not None:
                coords.append((lat, lon))
            else:
                logger.warning(f"Skipping row (invalid lat/lon): {row}")
                print(f"Skipping row (invalid lat/lon): {row}")
    logger.info(f"Loaded {len(coords)} valid coordinates from CSV.")    
    return coords

def main():
    logger.info("=== Starting main program ===")

    print("=== First Array ===")
    choice_1 = input("Enter 'csv' to load from file, or 'manual' to input manually: ").strip().lower()
    if choice_1 == "csv":
        array1 = load_points_csv("FIRST")
    else:
        array1 = get_points_manually("FIRST")
    
    print("\n=== Second Array ===")
    choice_2 = input("Enter 'csv' to load from file, or 'manual' to input manually: ").strip().lower()
    if choice_2 == "csv":
        array2 = load_points_csv("SECOND")
    else:
        array2 = get_points_manually("SECOND")

    if not array1 or not array2:
        logger.warning("One of the arrays is empty. Exiting early.")
        print("\nError: One of the arrays is empty. Exiting.")
    else:
        results = pair_arrays(array1, array2)
        print("\nResults:")
        for i, ((lat1, lon1), (closest_lat, closest_lon), dist) in enumerate(results, start=1):
            msg = (f"  - geo location #{i} in FIRST array ({lat1}, {lon1}) "
                   f"is closest to ({closest_lat}, {closest_lon}) "
                   f"with a distance of {dist:.2f} km.")
            logger.info(msg)
            print(msg)

    logger.info("=== Main program done ===")

# running the program without tracemalloc & cprofile         
# if __name__ == "__main__":
#     main()

# running program with tracemalloc & cprofile
if __name__ == "__main__":
    # Start memory profiling
    logger.info("Starting tracemalloc (memory profiler).")
    tracemalloc.start()

    # CPU profiling with cProfile
    logger.info("Starting CPU profiling with cProfile.")
    profiler = cProfile.Profile()
    profiler.enable()

    # Run main
    try:
        main()
    finally:
        # Stop CPU profiling
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats(pstats.SortKey.TIME)
        logger.info("CPU Profiling Results (top 20):")
        stats.print_stats(20)

        # Snap memory usage
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        logger.info("Memory Profiling Top 10 Lines:")
        for stat in top_stats[:10]:
            logger.info(stat)

        tracemalloc.stop()
        logger.info("Finished all profiling.")