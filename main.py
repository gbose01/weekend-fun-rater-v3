# main.py (formerly app.py)
from flask import Flask, request, jsonify, render_template
from utils.api_utils import get_place_details
from utils.scraping_utils import scrape_reddit_reviews
from utils.weather_utils import get_weekend_weather
from utils.gemini_utils import generate_gemini_review
from utils.entity_utils import extract_entities_with_gemini
from utils.travel_utils import get_travel_info
from utils.nlp_utils import analyze_sentiment, summarize_reviews


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_entity():
    try:
        data = request.get_json()
        query = data['query']
        print(f"DEBUG: Received query: {query}")

        entities = extract_entities_with_gemini(query)
        print(f"DEBUG: Extracted Entities: {entities}")

        if not entities:
            return jsonify({'error': 'Could not identify any places in your query'}), 400

        entities_data = []
        for entity in entities:
            place_info = get_place_details(entity)
            print(f"DEBUG: Google Places Info for {entity}: {place_info}")

            if place_info:
                latitude = place_info['geometry']['location']['lat']
                longitude = place_info['geometry']['location']['lng']

                reddit_reviews = scrape_reddit_reviews(place_info['name'], place_info['formatted_address'])
                print(f"DEBUG: Reddit Reviews for {entity}: {reddit_reviews}")

                all_reviews = []
                google_reviews = place_info.get('reviews', [])
                for review in google_reviews:
                    all_reviews.append(review.copy())
                for review in reddit_reviews:
                    all_reviews.append(review.copy())

                for review in all_reviews:
                    review['sentiment'] = analyze_sentiment(review['text'])

                positive_summary = summarize_reviews(all_reviews, "Positive")
                negative_summary = summarize_reviews(all_reviews, "Negative")

                weather_data = get_weekend_weather(latitude, longitude)
                print(f"DEBUG: Weather Data for {entity}: {weather_data}")

                entities_data.append({
                    'name': place_info['name'],
                    'reviews': all_reviews,  # Keep all reviews for display
                    'positive_summary': positive_summary,  # Add summary
                    'negative_summary': negative_summary,  # Add summary
                    'weather': weather_data,
                    'latitude': latitude,
                    'longitude': longitude
                })

            else:
                print(f"DEBUG: Could not retrieve place information for {entity}")
                # Consider how to handle this.  Maybe skip this entity?

        travel_info = None
        if len(entities_data) >= 2:
            lat1 = entities_data[0]['latitude']
            lon1 = entities_data[0]['longitude']
            lat2 = entities_data[1]['latitude']
            lon2 = entities_data[1]['longitude']
            travel_info = get_travel_info(lat1, lon1, lat2, lon2)
            print(f"DEBUG: Travel Info: {travel_info}")

        gemini_review = generate_gemini_review(entities_data, travel_info)
        print(f"DEBUG: Gemini Review: {gemini_review}")

        response_data = {
            'entities': entities_data,
            'travel_info': travel_info,
            'gemini_review': gemini_review
        }
        return jsonify(response_data), 200

    except Exception as e:
        print(f"ERROR in /search route: {type(e).__name__}: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# REMOVE OR COMMENT OUT THE if __name__ == '__main__': BLOCK
# if __name__ == '__main__':
#     app.run(debug=True)