# utils/entity_utils.py (Refined Prompt and Debugging)
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
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

def extract_entities_with_gemini(query):
    """
    Extracts place entities using the Gemini API (with a refined prompt).
    """
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""Extract all distinct named places and locations from the following user query.
The user is describing their plans for the weekend.

User Query: '{query}'

Return the results as a JSON array of strings.  Each string should be the
name of a place.  Do *NOT* include any descriptive words (like "hike", "lunch",
"trip", etc.).  Do *NOT* include any introductory text or explanations.
Do *NOT* include any conversational responses.  Output *ONLY* the JSON array.

Examples:

User Query: 'Eiffel Tower and Louvre Museum'
["Eiffel Tower", "Louvre Museum"]

User Query: 'restaurants in San Francisco'
["San Francisco"]

User Query: 'I want to go to Central Park'
["Central Park"]

User Query: 'I have no plans'  # Example with no entities
[]

User Query: 'mori point hike and then cheesecake factory for lunch'
["Mori Point", "Cheesecake Factory"]

Begin!
"""

    print(f"DEBUG: Gemini Prompt for Entity Extraction:\n{prompt}") # PRINT THE PROMPT

    try:
        response_text = make_api_call_with_retry(model, prompt)
        print(f"DEBUG: Gemini Raw Response: {response_text}")  # PRINT RAW RESPONSE

        if response_text:
            try:
                entities = json.loads(response_text)
                print(f"DEBUG: Parsed Entities: {entities}") # PRINT PARSED
                if isinstance(entities, list):
                    return entities
                else:
                    print(f"DEBUG: Gemini returned a non-list: {entities}")
                    return []
            except json.JSONDecodeError:
                print(f"DEBUG: Could not parse Gemini response as JSON: {response_text}")
                return []
        else:
            return []
    except Exception as e:
        print(f"Error extracting entities with Gemini: {type(e).__name__}: {e}")
        return []