import requests
import datetime
import pandas as pd

import firebase_admin
from firebase_admin import credentials, firestore

from bs4 import BeautifulSoup


def store_counts(url, firebase_credentials_file):
    counts = get_counts(url)

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials_file)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection = db.collection('gym_data_entries')

    cur_time = datetime.datetime.now()
    format_time = str(pd.Timestamp(cur_time))

    collection.document(format_time).set({
        'll_count': counts[0], 'ul_count': counts[1],
        'aq_count': counts[2],
    })


def get_counts(url):
    """
    Simple scraping function. Returns the current occupancy of the three areas of the gym.
    :param url: Website to scrape (RIT gym website)
    :return: list containing [ll_count, ul_count, aq_count]
    """
    req = requests.get(url)
    page = str(req.content, "windows-1250")
    soup = BeautifulSoup(page, 'html.parser')

    count_tags = soup.find_all("p", class_="occupancy-count")
    counts = [int(count_tag.getText()) for count_tag in count_tags[::2]]

    return counts
