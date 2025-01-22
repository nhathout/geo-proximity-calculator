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

    # Distance in km
    distance = distance / 1000
    return distance

def find_closest_point(ref_lat, ref_lon, array_of_coords):
    min_distance = None
    closest_point = None
    
    for (lat, lon) in array_of_coords:
        dist = haversine_distance(ref_lat, ref_lon, lat, lon)
        if min_distance is None or dist < min_distance:
            min_distance = dist
            closest_point = (lat, lon)
    
    return closest_point, min_distance

def main():
    print("Calculate the distance from a reference point to an array of points.")
    
    # prompt user for the single reference point
    ref_lat = float(input("Enter latitude of the reference point: "))
    ref_lon = float(input("Enter longitude of the reference point: "))
    
    # prompt user for the array of points
    num_points = int(input("How many points are in your array? "))
    array_of_coords = []
    
    for i in range(num_points):
        lat = float(input(f"Enter latitude of point #{i+1}: "))
        lon = float(input(f"Enter longitude of point #{i+1}: "))
        array_of_coords.append((lat, lon))
    
    # calculate & display the closest point
    closest_point, distance_in_meters = find_closest_point(ref_lat, ref_lon, array_of_coords)
    
    if closest_point is not None:
        print(f"\nClosest point is {closest_point} at a distance of {distance_in_meters:.2f} km.")
    else:
        print("No points were provided.")

if __name__ == "__main__":
    main()