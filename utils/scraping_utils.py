# utils/scraping_utils.py (Limit Reddit Reviews)
import praw
import os
from dotenv import load_dotenv
import time
import re

load_dotenv()

def scrape_reddit_reviews(place_name, place_address):
    """
    Scrapes Reddit comments for reviews, limited to 5 reviews.
    """
    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        user_agent=os.environ.get("REDDIT_USER_AGENT"),
    )

    address_parts = place_address.split(',')
    city = ""
    if len(address_parts) > 1:
        city = address_parts[-2].strip()

    subreddits_to_search = ["travel"]
    if city:
        subreddits_to_search.append(city.replace(" ", "").lower())
    if place_name:
        subreddits_to_search.append(place_name.replace(" ", "").lower())

    if "restaurant" in place_name.lower() or "food" in place_name.lower() or "cafe" in place_name.lower():
        subreddits_to_search.extend(["food", "restaurants", "eats"])
    if "museum" in place_name.lower():
        subreddits_to_search.extend(["museums", "art", "history"])
    if "park" in place_name.lower():
        subreddits_to_search.extend(["parks", "outdoors"])

    subreddits_to_search = list(set(subreddits_to_search))

    reviews = []
    try:
        for subreddit_name in subreddits_to_search:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                search_query = f'"{place_name}"'
                for submission in subreddit.search(search_query, limit=5): # Limit submissions
                    submission.comments.replace_more(limit=0)
                    comment_count = 0 # Limit comments per submission
                    for comment in submission.comments.list():
                        if any(keyword in comment.body.lower() for keyword in ["visited", "recommend", "experience", "good", "bad", "review"]):
                            if len(comment.body.split()) > 5:
                                reviews.append({
                                    'source': f'Reddit (r/{subreddit_name})',
                                    'text': comment.body,
                                    'rating': None,
                                    'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(comment.created_utc)),
                                    'user': str(comment.author) if comment.author else "[deleted]",
                                })
                                comment_count += 1
                                if comment_count >= 5:  # Limit comments per submission
                                    break
                        if len(reviews) >= 5: # Limit overall reviews
                            break
                    if len(reviews) >=5:
                        break

            except Exception as e:
                print(f"Error accessing subreddit r/{subreddit_name}: {type(e).__name__} - {e}")
                continue
            if len(reviews) >= 5:
                break
    except Exception as e:
        print("Error: ", e)

    return reviews