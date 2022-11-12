"""
File: main.py
Author: Nicholas Gardner <nag6650@rit.edu>

Entry point for Google Cloud Run.

Scrapes occupancy count for 3 RIT gym facilities,
creates predictions using Prophet,
then stores updated counts and predictions in a Firestore DB.
"""

from scrape_and_store import get_counts, store_counts


def main(event_data, context):
    """
    Main function wrapper (required by Google Cloud Run)
    :param event_data: Required parameter for Google Cloud Run
    :param context: Required parameter for Google Cloud Run
    :return: None
    """
    counts = get_counts()
    store_counts(counts)
