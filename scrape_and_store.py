import requests
import datetime
import pandas as pd
import pytz

import firebase_admin
from firebase_admin import credentials, firestore

from bs4 import BeautifulSoup


def store_counts(url, firebase_credentials_file, timezone):
    """
    Triggers a scrape and stores the resulting counts in a firebase db
    :param url: url to scrape
    :param firebase_credentials_file: credentials file to access db
    :return: None
    """
    counts = get_counts(url)

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials_file)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection = db.collection('gym_data_entries')

    cur_time = datetime.datetime.now()
    format_time = str(pd.Timestamp(cur_time).tz_localize('UTC').astimezone(pytz.timezone(timezone)))

    dates = collection.document('date').get().to_dict()['entries']
    dates.append(format_time)
    collection.document('date').update({
        'entries': dates
    })

    lower_level = collection.document('lower_level').get().to_dict()['entries']
    lower_level.append(counts[0])
    collection.document('lower_level').update({
        'entries': lower_level
    })

    upper_level = collection.document('upper_level').get().to_dict()['entries']
    upper_level.append(counts[1])
    collection.document('upper_level').update({
        'entries': upper_level
    })

    aquatic_center = collection.document('aquatic_center').get().to_dict()['entries']
    aquatic_center.append(counts[2])
    collection.document('aquatic_center').update({
        'entries': aquatic_center
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
