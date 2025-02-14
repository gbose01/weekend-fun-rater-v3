# utils/travel_utils.py
import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()
gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))

def get_travel_info(origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Gets travel time and distance between two locations using the Distance Matrix API.
    Args:
        origin_lat: Latitude of the origin.
        origin_lon: Longitude of the origin.
        dest_lat: Latitude of the destination.
        dest_lon: Longitude of the destination.
    Returns:
        A dictionary with 'distance' (text) and 'duration' (text), or None on error.
    """
    try:
        result = gmaps.distance_matrix(
            origins={"latitude": origin_lat, "longitude": origin_lon},
            destinations={"latitude": dest_lat, "longitude": dest_lon},
            mode="driving",  # You can change to "walking", "bicycling", "transit"
            units="imperial" # or "metric"
        )

        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            distance = result['rows'][0]['elements'][0]['distance']['text']
            duration = result['rows'][0]['elements'][0]['duration']['text']
            return {'distance': distance, 'duration': duration}
        else:
            print(f"Distance Matrix API error: {result['status']}")
            return None

    except Exception as e:
        print(f"Error in get_travel_info: {type(e).__name__}: {e}")
        return None