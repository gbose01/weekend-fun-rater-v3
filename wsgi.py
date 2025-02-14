# wsgi.py
from main import app as application  # Import the 'app' object from main.py

# The if __name__ == '__main__': block is NOT needed for Gunicorn and should be removed.
# Gunicorn directly imports the 'application' object.