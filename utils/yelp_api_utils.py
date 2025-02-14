# utils/yelp_api_utils.py
import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode
import time

load_dotenv()

YELP_API_KEY = os.environ.get("YELP_API_KEY")
BASE_URL = "https://api.yelp.com/v3"


def _yelp_api_request(endpoint, params=None):
    """
    Makes an authenticated request to the Yelp Fusion API.
    """
    url = BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}",
    }
    if params:
        url += "?" + urlencode(params)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Yelp API request error: {e}")
        print(f"  URL: {url}")
        return None
    except ValueError as e:
        print(f"Error decoding Yelp API response as JSON: {e}")
        return None


def get_yelp_reviews(place_name, place_address, latitude, longitude):
    """Retrieves Yelp reviews using the Yelp Fusion API (Business Match)."""

    if not all([place_name, place_address, latitude, longitude]):
        print("Missing required parameters for Yelp Business Match.")
        return []

    address_parts = place_address.split(',')
    street = ""
    city = ""
    state = ""
    zip_code = ""

    if len(address_parts) >= 3:
        street = address_parts[0].strip()
        city = address_parts[1].strip()
        state_and_zip = address_parts[2].strip().split()
        if(len(state_and_zip) > 0):
            state = state_and_zip[0]
        if(len(state_and_zip) > 1):
            zip_code = state_and_zip[1]

    elif len(address_parts) == 2:
        city = address_parts[0].strip()
        state_and_zip = address_parts[1].strip().split()
        if(len(state_and_zip) > 0):
            state = state_and_zip[0]
        if(len(state_and_zip) > 1):
            zip_code = state_and_zip[1]
    # --- 1. Business Match (Use the Match endpoint) ---
    match_params = {
        'name': place_name,
        'address1': street,  # Street address
        'city': city,
        'state': state,
        'country': 'US',  # Yelp is primarily US-focused; adjust if needed.
        'latitude': latitude,
        'longitude': longitude,
        'match_threshold': 'default', #Added for better matching
    }

    # Clean up empty parameters to prevent errors
    filtered_match_params = {k: v for k, v in match_params.items() if v}

    match_results = _yelp_api_request("/businesses/matches", params=filtered_match_params)

    if not match_results or 'businesses' not in match_results or not match_results['businesses']:
        print("Business not found on Yelp via Business Match.")
        return []

    business_id = match_results['businesses'][0]['id']

    # --- 2. Check Business Details (Optional, but good for debugging) ---
    business_details = _yelp_api_request(f"/businesses/{business_id}")
    if not business_details:
        print(f"Could not retrieve details for business ID: {business_id}")
        return []
    #print(f"DEBUG: Business Details: {business_details}")  # Uncomment to see details


    # --- 3. Get Reviews (Handle 404 Specifically) ---
    review_results = _yelp_api_request(f"/businesses/{business_id}/reviews")

    if review_results is None:  # General API error (already handled)
        return []
    #We handle the case where no reviews are available
    if 'error' in review_results and review_results['error']['code'] == 'NOT_FOUND':
        print(f"No reviews found for business ID: {business_id} (Yelp API 404)")
        return []
    elif 'reviews' in review_results:
        reviews = []
        for review in review_results['reviews']:
            review_data = {
                'source': 'Yelp',  # *** ENSURE THIS IS HERE ***
                'text': review['text'],
                'rating': review['rating'],
                'date': review['time_created'],
                'user': review['user']['name'] if review.get('user') and review['user'].get('name') else None,
            }
            #print(f"DEBUG: Processed Yelp review: {review_data}")  # Keep for debugging if needed
            reviews.append(review_data)
        return reviews
    else: #Handles other errors, like a malformed request.
        print(f"Unexpected response from Yelp reviews endpoint: {review_results}")
        return[]

if __name__ == '__main__':
    # Philz Coffee Example
    test_name = "Philz Coffee"
    test_address = "3101 24th St, San Francisco, CA 94110"
    latitude = 37.75252
    longitude = -122.41436

    reviews = get_yelp_reviews(test_name, test_address, latitude, longitude)

    if reviews:
        print(f"Found {len(reviews)} Yelp reviews for {test_name}:")
        for review in reviews:
            print(review)  # Print the ENTIRE review dictionary
    else:
        print(f"No Yelp reviews found for {test_name}.")