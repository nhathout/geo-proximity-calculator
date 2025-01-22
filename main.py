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
    return distance

def main():
    print("Calculate the distance between two geographic points.")
    lat1 = float(input("Enter latitude of point 1: "))
    lon1 = float(input("Enter longitude of point 1: "))
    lat2 = float(input("Enter latitude of point 2: "))
    lon2 = float(input("Enter longitude of point 2: "))

    distance_in_meters = haversine_distance(lat1, lon1, lat2, lon2)
    print(f"\nDistance between these points: {distance_in_meters:.2f} meters")

if __name__ == "__main__":
    main()