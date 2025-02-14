# utils/nlp_utils.py
from flair.models import TextClassifier
from flair.data import Sentence
from transformers import pipeline

# Load the Flair sentiment classifier (downloads automatically the first time)
classifier = TextClassifier.load('en-sentiment')

# Initialize the Hugging Face summarizer (downloads the model the first time)
summarizer = pipeline("summarization")

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a review text using Flair.

    Args:
        text: The review text.

    Returns:
        A string representing the sentiment.
    """
    sentence = Sentence(text)
    classifier.predict(sentence)
    label = sentence.labels[0]  # Get the top label (e.g., 'POSITIVE', 'NEGATIVE')
    score = sentence.labels[0].score  # Get the confidence score

    if label.value == 'POSITIVE':
        if score > 0.9:
            return 'Highly Positive'
        else:
            return 'Positive'
    elif label.value == 'NEGATIVE':
        if score > 0.9:
            return 'Highly Negative'
        else:
            return 'Negative'
    else:
        return 'Neutral' # Should not happen with en-sentiment, but good practice

def summarize_reviews(reviews, sentiment_category, max_length=130, min_length=30):
    """
    Summarizes reviews using Hugging Face Transformers.
    """
    if not reviews:
        return "No reviews available to summarize."

    relevant_reviews = [
        review['text'] for review in reviews
        if review['sentiment'] in ('Positive', 'Highly Positive')
        and sentiment_category == "Positive"
    ]
    relevant_reviews += [
        review['text'] for review in reviews
        if review['sentiment'] in ('Negative', 'Highly Negative')
        and sentiment_category == "Negative"
    ]

    if not relevant_reviews:
        return f"No {sentiment_category} reviews to summarize."

    combined_text = " ".join(relevant_reviews)

    try:
        summary = summarizer(combined_text, max_length=max_length, min_length=min_length)[0]['summary_text']
        return summary
    except IndexError:  # Handle empty summary case
        return f"No {sentiment_category} summary available."
    except Exception as e:
        print(f"Error during summarization: {type(e).__name__}: {e}")
        return f"Error generating {sentiment_category} summary."


if __name__ == '__main__':
    # --- Test Suite ---
    print("-" * 30)
    print("Testing utils/nlp_utils.py")
    print("-" * 30)

    test_reviews = [
        {"text": "This place is absolutely amazing! The best experience ever.", "sentiment": "Highly Positive"},
        {"text": "The food was pretty good. I enjoyed it.", "sentiment": "Positive"},
        {"text": "It was okay. Nothing special.", "sentiment": "Neutral"},
        {"text": "The service was slow and the food was cold.", "sentiment": "Negative"},
        {"text": "Absolutely terrible!  Worst restaurant I've ever been to!", "sentiment": "Highly Negative"},
        {"text": "I had a mediocre experience.  It wasn't bad, but it wasn't great either.", "sentiment": "Neutral"},
        {"text": "The ambiance was fantastic, and the staff were incredibly friendly.", "sentiment": "Positive"},
        {"text": "I was disappointed with the quality of the product.", "sentiment": "Negative"},
         {"text": "This is a very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very long review.", "sentiment": "Neutral"}, # Test long reviews
    ]

    print("\n--- Sentiment Analysis Tests ---")
    for review in test_reviews:
        predicted_sentiment = analyze_sentiment(review['text'])
        print(f"  Review: '{review['text'][:50]}...'")  # Show first 50 chars
        print(f"    Expected Sentiment: {review['sentiment']}")
        print(f"    Predicted Sentiment: {predicted_sentiment}")
        assert predicted_sentiment == review['sentiment'], f"Sentiment mismatch! Expected {review['sentiment']}, got {predicted_sentiment}" #Checks for accuracy
        print("    PASSED")


    print("\n--- Summarization Tests ---")
    positive_summary = summarize_reviews(test_reviews, "Positive")
    print(f"  Positive Summary:\n{positive_summary}")

    negative_summary = summarize_reviews(test_reviews, "Negative")
    print(f"  Negative Summary:\n{negative_summary}")

    empty_summary = summarize_reviews([], "Positive")  # Test empty reviews
    print(f"  Empty Summary: {empty_summary}")

    no_positive = summarize_reviews([r for r in test_reviews if r['sentiment'] == 'Negative'], "Positive")
    print(f"No Positive Reviews Summary: {no_positive}")
    print("-" * 30)
    print("All tests completed.")