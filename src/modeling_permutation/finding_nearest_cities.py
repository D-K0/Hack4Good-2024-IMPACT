'''
    file descritption
'''
import math

def find_nearest_cities(city_list, n=4):

    """
    Find the nearest cities for a given list of cities based on geographical coordinates.

    Parameters:
        city_list (list of str): A list of city names for which to find the nearest cities.
        n (int): The number of nearest cities to return for each city in the list. Default is 4.

    Returns:
        dict: A dictionary where each key is a city from the input list and the value is a list of
              the `n` nearest cities. If a city is not found in the predefined list of cities,
              the value will be an empty list.

    Functionality:
        This function calculates the geographical distance between cities using the Haversine formula,
        which accounts for the curvature of the Earth. It takes the input list of cities, retrieves their
        coordinates, and then computes the distance to all other cities in the predefined set. The
        resulting nearest cities are sorted by distance, and the closest `n` cities are returned.
    """

    # Coordinates of the cities
    cities = {
        "Aleppo": (36.2021, 37.1343),
        "Al-Hasakeh": (36.5, 40.7333),
        "Ar-Raqqa": (35.947, 39.017),
        "Damascus": (33.5138, 36.2765),
        "Dar'a": (32.6163, 36.1),
        "Deir-ez-Zor": (35.3315, 40.148),
        "Hama": (35.1312, 36.7572),
        "Homs": (34.7343, 36.7123),
        "Idleb": (35.9318, 36.6317),
        "Lattakia": (35.7837, 35.5),
        "Quneitra": (33.2, 35.5),
        "Rural Damascus": (33.6, 36.5),
    }

    def haversine(coord1, coord2):

    # Radius of the Earth in kilometers
        R = 6371.0
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             (math.sin(dlon / 2) ** 2))
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    nearest_cities = {}

    for city in city_list:
        if city in cities:
            coord = cities[city]
            distances = {}
            for other_city, other_coord in cities.items():
                if city != other_city:
                    distance = haversine(coord, other_coord)
                    distances[other_city] = distance
                    
             # Sort by distance and take the 'n' nearest cities
            nearest_cities[city] = sorted(distances, key=distances.get)[:n]
        else:
            nearest_cities[city] = []

    return nearest_cities



