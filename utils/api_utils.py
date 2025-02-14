# utils/api_utils.py
import os
import googlemaps
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))

def get_place_details(query):
    """
    Retrieves place ID and details from the Google Places API.
    Adds 'source': 'Google' to each review, and limits to 5 reviews.
    """
    try:
        # 1. Find Place (to get the place_id)
        places_result = gmaps.find_place(
            input=query,
            input_type="textquery",
            fields=["place_id", "name", "formatted_address", "geometry"]  # Get geometry
        )

        if places_result["status"] == "OK" and places_result["candidates"]:
            place_id = places_result["candidates"][0]["place_id"]
            place_name = places_result["candidates"][0]["name"]
            place_address = places_result["candidates"][0]["formatted_address"]
            geometry = places_result["candidates"][0]['geometry']
            location = geometry['location']
            latitude = location['lat']
            longitude = location['lng']


            # 2. Place Details
            place_details = gmaps.place(
                place_id=place_id,
                fields=["name", "formatted_address", "rating", "website", "formatted_phone_number", "review"]
            )

            if place_details["status"] == "OK":
                result = place_details["result"]
                reviews = []
                # Limit to 5 reviews AND ensure reviews exist
                for review in result.get("reviews", [])[:5]:  # Limit to 5 reviews
                    review_data = {
                        'source': 'Google',
                        'text': review.get('text'),
                        'rating': review.get('rating'),
                        'date': review.get('relative_time_description'),
                        'user': review.get('author_name')
                    }
                    reviews.append(review_data)

                return_val = {
                    "place_id": place_id,
                    "name": result.get("name"),
                    "formatted_address": result.get("formatted_address"),
                    "rating": result.get("rating"),
                    "website": result.get("website"),
                    "formatted_phone_number": result.get("formatted_phone_number"),
                    "reviews": reviews,  # Limited reviews
                    "geometry": geometry
                }
                return return_val
            else:
                print(f"Error getting place details: {place_details['status']}")
                return None
        elif places_result["status"] == "ZERO_RESULTS":
            print("No results found for that query.")
            return None
        else:
            print(f"Error in Find Place search: {places_result['status']}")
            return None

    except Exception as e:
        print(f"An unexpected error occurred in get_place_details: {type(e).__name__}: {e}")
        return None