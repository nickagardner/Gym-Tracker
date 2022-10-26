"""
File: main.py
Author: Nick Gardner <nag6650@rit.edu>
Script run by Google Cloud Run to scrape RIT's recreation website for gym data,
store that data in a Google Firestore NoSQL database, then render the results with plotly.
This produces a figure that is available online and is embedded in my website.
"""

from scrape_and_store import store_counts

# Constants
RIT_GYM_URL = "https://recreation.rit.edu/facilityoccupancy"
TIMEZONE = "US/Eastern"
# These credentials files are created during the walkthrough setup for both Firebase and Plotly
FIREBASE_CREDENTIALS_FILE = "firebase_credentials.json"


def main(event_data, context):
    """
    Main function wrapper (required by Google Cloud Run)
    :param event_data: Required parameter for Google Cloud Run
    :param context: Required parameter for Google Cloud Run
    :return: None
    """
    store_counts(RIT_GYM_URL, FIREBASE_CREDENTIALS_FILE, TIMEZONE)