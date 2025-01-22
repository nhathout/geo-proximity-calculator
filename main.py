import math

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

if __name__ == "__main__":
    # prompt user for the FIRST array
    num_points_1 = int(input("How many geo locations are in your FIRST array? "))
    array1 = []
    for i in range(num_points_1):
        lat = float(input(f"Enter latitude of geo location #{i+1} in FIRST array: "))
        lon = float(input(f"Enter longitude of geo location #{i+1} in FIRST array: "))
        
        array1.append((lat, lon))
    
    # prompt user for the SECOND array
    num_points_2 = int(input("How many geo locations are in your SECOND array? "))
    array2 = []
    for i in range(num_points_2):
        lat = float(input(f"Enter latitude of geo location #{i+1} in SECOND array: "))
        lon = float(input(f"Enter longitude of geo location #{i+1} in SECOND array: "))
        
        array2.append((lat, lon))

    # match array1 points to their closest points in array2
    results = pair_arrays(array1, array2)

    # print results
    print("\nResults:")
    for i, ((lat1, lon1), (closest_lat, closest_lon), dist) in enumerate(results, start=1):
        print(f"  - geo location #{i} in FIRST array ({lat1}, {lon1}) "
              f"is closest to ({closest_lat}, {closest_lon}) in SECOND array "
              f"with a distance of {dist:.2f} km.")