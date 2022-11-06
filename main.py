"""
File: main.py
Author: Nick Gardner <nag6650@rit.edu>
"""

from scrape_and_store import store_counts, get_counts

# Constants
RIT_GYM_URL = "https://recreation.rit.edu/facilityoccupancy"
TIMEZONE = "US/Eastern"


def main(event_data, context):
    """
    Main function wrapper (required by Google Cloud Run)
    :param event_data: Required parameter for Google Cloud Run
    :param context: Required parameter for Google Cloud Run
    :return: None
    """
    counts = get_counts(RIT_GYM_URL)
    store_counts(counts, TIMEZONE)
