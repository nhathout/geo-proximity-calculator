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

if __name__ == "__main__":
    # prompt user for the FIRST array
    num_points_1 = get_valid_input("How many geo locations are in your FIRST array? ", min_val=1)
    num_points_1 = int(num_points_1)  # safe to convert to int after validation
    
    array1 = []
    for i in range(num_points_1):
        lat = get_valid_input(f"Enter latitude of geo location #{i+1} in FIRST array: ", min_val=-90, max_val=90)
        lon = get_valid_input(f"Enter longitude of geo location #{i+1} in FIRST array: ", min_val=-180, max_val=180)
        array1.append((lat, lon))
    
    # prompt user for the SECOND array
    num_points_2 = get_valid_input("How many geo locations are in your SECOND array? ", min_val=1)
    num_points_2 = int(num_points_2)
    
    array2 = []
    for i in range(num_points_2):
        lat = get_valid_input(f"Enter latitude of geo location #{i+1} in SECOND array: ", min_val=-90, max_val=90)
        lon = get_valid_input(f"Enter longitude of geo location #{i+1} in SECOND array: ", min_val=-180, max_val=180)
        array2.append((lat, lon))

    results = pair_arrays(array1, array2)

    print("\nResults:")
    for i, ((lat1, lon1), (closest_lat, closest_lon), dist) in enumerate(results, start=1):
        print(f"  - geo location #{i} in FIRST array ({lat1}, {lon1}) "
              f"is closest to ({closest_lat}, {closest_lon}) "
              f"with a distance of {dist:.2f} km.")