import googlemaps
import environ
from math import radians, cos, sin, sqrt, atan2


def calculate_geodesic_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert coordinates from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def calculate_distance(origin, destination):
    env = environ.Env()
    environ.Env.read_env()
    gmaps = googlemaps.Client(key=env("GOOGLE_MAPS_KEY"))
    distance_matrix = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="walking")
    distance = distance_matrix['rows'][0]['elements'][0]['distance']['value']  # Distance in meters
    return distance


def get_coordinates_from_address(address):
    env = environ.Env()
    environ.Env.read_env()
    gmaps = googlemaps.Client(key=env("GOOGLE_MAPS_KEY"))
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        latitude = geocode_result[0]["geometry"]["location"]["lat"]
        longitude = geocode_result[0]["geometry"]["location"]["lng"]
        return latitude, longitude
    return None, None