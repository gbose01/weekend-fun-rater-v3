# utils/gemini_utils.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
import random

load_dotenv()

def make_api_call_with_retry(model, prompt, max_retries=5):
    """
    Makes an API call with exponential backoff for rate limiting.
    """
    retries = 0
    delay = 1  # Initial delay in seconds

    while retries < max_retries:
        try:
            response = model.generate_content(prompt)
            return response.text  # Success!
        except Exception as e:
            if "ResourceExhausted" in str(e) or "429" in str(e):  # Check for rate limit
                retries += 1
                wait_time = delay * (2 ** retries) + random.uniform(0, 1)  # Exponential backoff + jitter
                print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Other error: {type(e).__name__}: {e}")
                return None  # Non-rate-limit error

    print(f"Max retries exceeded.")
    return None


def generate_gemini_review(entities_data, travel_info=None):
    """
    Generates a review using the Gemini model, with improved prompt and error handling.
    Now expects *summaries* in entities_data.
    """
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')

    prompt = """You are an expert travel planner specializing in creating concise and informative weekend trip summaries.

Your task is to analyze the provided information and generate a short, helpful review of a user's proposed weekend trip. Focus on the feasibility and overall quality of the plan, considering the provided review *summaries*, weather, and (if available) travel time between locations.

**Here's the information you MUST use:**

"""

    for i, entity_data in enumerate(entities_data):
        prompt += f"\n**Destination {i+1}: {entity_data['name']}**\n"

        # Use summaries instead of raw reviews
        prompt += "\n*Review Summary (Positive):*\n"
        prompt += entity_data.get('positive_summary', '- No positive summary available.\n')
        prompt += "\n*Review Summary (Negative):*\n"
        prompt += entity_data.get('negative_summary', '- No negative summary available.\n')


        prompt += "\n*Weekend Weather Forecast:*\n"
        if entity_data['weather']:
            for day, forecast in entity_data['weather'].items():
                prompt += f"- {day}: Date: {forecast.get('date', 'N/A')}, Temperature: {forecast.get('temperature', 'N/A')}°F, Description: {forecast.get('description', 'N/A')}\n"
        else:
            prompt += "- No weather data available.\n"

    if travel_info and len(entities_data) > 1:
        prompt += f"\n**Travel Information (between {entities_data[0]['name']} and {entities_data[1]['name']}):**\n"
        prompt += f"- Distance: {travel_info.get('distance', 'N/A')}\n"
        prompt += f"- Duration: {travel_info.get('duration', 'N/A')}\n"
    elif len(entities_data) > 1:
        prompt += f"\n**Travel Information:** No travel information available, as multiple destinations were found. Please ensure the destinations are close together.\n"

    prompt += """

**Your Task:**

1.  **Catchy One-Liner:**  FIRST, create a *single*, catchy, and descriptive sentence that summarizes the overall rating of the weekend plan.  This should be short and attention-grabbing.
2.  **Overall Assessment:** Provide a concise overall assessment of the weekend plan (Is it feasible?  Too rushed?  Well-balanced?).
3.  **Pros and Cons:** Briefly list the *most significant* pros and cons of the plan, based on the reviews and weather.  Don't just repeat the reviews; synthesize them.
4.  **Recommendations (Optional):** If appropriate, offer *brief*, specific suggestions for improvement (e.g., "Consider visiting X instead of Y on Sunday due to the weather forecast.").
5. **Travel Practicality:** If travel information is available, comment on its practicality.
6.  **Rating:** Give the overall plan a rating out of 5 stars. Be realistic, based on the provided information.

**Output Format:**
Give your response in the following format.

## Weekend Plan Review: [Destination(s)]

**Catchy One-Liner:** [Your one-liner here]

**Overall Assessment:**

[Your concise overall assessment here]

**Pros:**

* [Pro 1]
* [Pro 2]
* [Pro 3]

**Cons:**

* [Con 1]
* [Con 2]

**Recommendations (Optional):**

[Your recommendations here]

**Rating:** ⭐⭐⭐⭐ (Example - out of 5 stars)
"""

    try:
        # Use the retry function
        review_text = make_api_call_with_retry(model, prompt)
        return review_text
    except Exception as e:
        print(f"Error generating Gemini review: {type(e).__name__}: {e}")
        return None