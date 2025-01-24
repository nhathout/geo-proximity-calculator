# geo-proximity-calculator

**Mission of the module:**  If the user gives you two arrays of geo location, match each point in the first array to the closest one in the second array.

## Getting Started:

1. Clone & Enter the Repository:<br>
```git clone https://github.com/nhathout/geo-proximity-calculator.git```<br>
```cd geo-proximity-calculator```

2. Run the program:<br>
```python3 main.py```

## Solution Design:

1. **haversine_distance(lat1, lon1, lat2, lon2)**
    - credit to [https://www.movable-type.co.uk/scripts/latlong.html](https://www.movable-type.co.uk/scripts/latlong.html) :

![haversine-formula](haversine.png)

2. **find_closest_point(temp_lat, temp_lon, array_of_coords)**
    - "array-to-point"
    - takes a temp point (temp_lat & temp_lon) and a list of coordinates and returns the closest coordinate and the distance to that coordinate.

3. **pair_arrays(array1, array2)**
    - "array-to-array"
    - iterates over each point in array1 calling find_closestpoint() with array2 as the inputs. 
    - returns list of matched pairs and their respective distances.
