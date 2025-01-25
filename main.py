import math

# function to calculate Haversine distance between to geo locations
def haversine_distance(lat1, lon1, lat2, lon2):
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
    return distance_km

# function to find closest point in an array of points to a reference point
def find_closest_point(temp_lat, temp_lon, array_of_coords):
    min_distance = None
    closest_point = None
    
    for (lat, lon) in array_of_coords:
        dist = haversine_distance(temp_lat, temp_lon, lat, lon)
        if min_distance is None or dist < min_distance:
            min_distance = dist
            closest_point = (lat, lon)
    
    return closest_point, min_distance

# function that, for each (lat, lon) in array1, it finds the closest point in array2
# returns: [((lat1, lon1), closestLat, closestLon), distanceInKm), ( same for point 2 )]
def pair_arrays(array1, array2):
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

        try:
            val = float(user_input)
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"Error: value {val} out of range. Must be between {min_val} and {max_val}.")
                continue
            return val
        except ValueError:
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
    return decimal_degrees

def get_point(is_lat=True):
    label = "latitude" if is_lat else "longitude"

    while True:
        choice = input(f"Do you want to enter {label} in decimal (d) or DMS (dm)? [d/dm]: ").strip().lower()
        if choice == "d":
            # decimal
            d_min, d_max = (-90, 90) if is_lat else (-180, 180)
            return get_valid_input(f"Enter {label} in decimal degrees: ", d_min, d_max)
        elif choice == "dm":
            return get_dms(is_lat=is_lat)
        else:
            print("Invalid choice. Type 'd' or 'dm'.")

if __name__ == "__main__":
    # prompt user for the FIRST array
    num_points_1 = get_valid_input("How many geo locations are in your FIRST array? ", min_val=1)
    num_points_1 = int(num_points_1)
    
    array1 = []
    for i in range(num_points_1):
        print(f"\nFIRST array: Enter coordinates for point #{i+1}.")
        lat = get_point(is_lat=True)
        lon = get_point(is_lat=False)
        array1.append((lat, lon))
    
    # prompt user for the SECOND array
    num_points_2 = get_valid_input("How many geo locations are in your SECOND array? ", min_val=1)
    num_points_2 = int(num_points_2)
    
    array2 = []
    for i in range(num_points_2):
        print(f"\nSECOND array: Enter points for point #{i+1}.")
        lat = get_point(is_lat=True)
        lon = get_point(is_lat=False)
        array2.append((lat, lon))

    results = pair_arrays(array1, array2)

    print("\nResults:")
    for i, ((lat1, lon1), (closest_lat, closest_lon), dist) in enumerate(results, start=1):
        print(f"  - geo location #{i} in FIRST array ({lat1}, {lon1}) "
              f"is closest to ({closest_lat}, {closest_lon}) "
              f"with a distance of {dist:.2f} km.")