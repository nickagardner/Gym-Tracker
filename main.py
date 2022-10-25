"""
File: main.py
Author: Nick Gardner <nag6650@rit.edu>
Script run by Google Cloud Run to scrape RIT's recreation website for gym data,
store that data in a Google Firestore NoSQL database, then render the results with plotly.
This produces a figure that is available online and is embedded in my website.
"""

import requests
import datetime
import pytz
import pandas as pd
import numpy as np

import json

import firebase_admin
from firebase_admin import credentials, firestore

from bs4 import BeautifulSoup

import chart_studio
import chart_studio.plotly as py
import plotly.graph_objects as go

# Constants
RIT_GYM_URL = "https://recreation.rit.edu/facilityoccupancy"

# These credentials files are created during the walkthrough setup for both Firebase and Plotly
FIREBASE_CREDENTIALS_FILE = "firebase_credentials.json"
PLOTLY_CREDENTIALS_FILE = "plotly_credentials.json"


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


def store_counts(counts, firebase_cred_file):
    """
    Stores scraped occupancy counts in a firestore database
    :param counts: Scraped counts
    :param firebase_cred_file: Credentials file to log in to database
    :return: None
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_cred_file)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection = db.collection('gym_data_entries')

    cur_time = datetime.datetime.now()
    format_time = str(pd.Timestamp(cur_time))

    collection.document(format_time).set({
        'll_count': counts[0], 'ul_count': counts[1],
        'aq_count': counts[2],
    })


def render_plot(plotly_cred_file, firebase_cred_file):
    """
    Renders figure with gym data.
    :param plotly_cred_file: Credential file to send to chart studio to plot online
    :param firebase_cred_file: Credential file to read data from Firebase
    :return: None
    """
    cred_file = open(plotly_cred_file)
    creds = json.load(cred_file)
    chart_studio.tools.set_credentials_file(username=creds["username"], api_key=creds["api_key"])
    chart_studio.tools.set_config_file(world_readable=True, sharing='public')

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_cred_file)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection = db.collection('gym_data_entries')

    docs = collection.get()
    num_docs = len(docs)
    x = np.empty([num_docs], pd.Timestamp)
    ll_y = np.empty([num_docs])
    ul_y = np.empty([num_docs])
    aq_y = np.empty([num_docs])
    for i, doc in enumerate(docs):
        data = doc.to_dict()
        x[i] = pd.Timestamp(doc.id).tz_localize('UTC').astimezone(pytz.timezone('US/Eastern'))
        ll_y[i] = data["ll_count"]
        ul_y[i] = data["ul_count"]
        aq_y[i] = data["aq_count"]

    df = pd.DataFrame({'date': x, 'll_count': ll_y, 'ul_count': ul_y, 'aq_count': aq_y})

    today_date = datetime.date.today()
    today_begin = pd.Timestamp(tz=pytz.timezone('US/Eastern'), year=today_date.year,
                               month=today_date.month, day=today_date.day)
    tomorrow_date = today_date + datetime.timedelta(days=1)
    tomorrow_begin = pd.Timestamp(tz=pytz.timezone('US/Eastern'), year=tomorrow_date.year,
                                  month=tomorrow_date.month, day=tomorrow_date.day)

    df_daily = df[(df['date'] >= today_begin) & (df['date'] <= tomorrow_begin)]

    now = datetime.datetime.now()
    monday = now - datetime.timedelta(days=now.weekday())
    week_begin = pd.Timestamp(tz=pytz.timezone('US/Eastern'), year=monday.year,
                              month=monday.month, day=monday.day)
    next_monday = monday + datetime.timedelta(days=7)
    week_end = pd.Timestamp(tz=pytz.timezone('US/Eastern'), year=next_monday.year,
                            month=next_monday.month, day=next_monday.day)


    df_weekly = df[(df['date'] >= week_begin) & (df['date'] <= week_end)]
    df_weekly = df_weekly.set_index('date').resample('6h').mean().reset_index()

    fig = go.Figure()

    format_column_names = ["Lower Level", "Upper Level", "Aquatic Center"]
    visibility = [False, True]
    for df_idx, df in enumerate([df_weekly, df_daily]):
        for col_idx, column in enumerate(["ll_count", "ul_count", "aq_count"]):
            fig.add_trace(go.Scatter(x=df["date"], y=df[column],
                                     mode='lines+markers',
                                     name=format_column_names[col_idx],
                                     visible=visibility[df_idx]))

    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons=list(
                [dict(label='Daily',
                      method='update',
                      args=[{'visible': [False, False, False, True, True, True]},
                            {'xaxis.range': [today_begin, tomorrow_begin]}]),
                 dict(label='Weekly',
                      method='update',
                      args=[{'visible': [True, True, True, False, False, False]},
                            {'xaxis.range': [week_begin, week_end]}])
                 ])
        )
        ]
    )

    fig.update_xaxes(range=[today_begin, tomorrow_begin])
    fig.update_layout(title="RIT Recreation Facility Occupancy", xaxis_title="Datetime",
                      yaxis_title="Number of Occupants", legend_title="Facility Name")

    py.plot(fig, filename='RIT_gym_occupancy', auto_open=False)


def main(event_data, context):
    """
    Main function wrapper (required by Google Cloud Run)
    :param event_data: Required parameter for Google Cloud Run
    :param context: Required parameter for Google Cloud Run
    :return: None
    """
    counts = get_counts(RIT_GYM_URL)
    store_counts(counts, FIREBASE_CREDENTIALS_FILE)
    render_plot(PLOTLY_CREDENTIALS_FILE, FIREBASE_CREDENTIALS_FILE)


# Uncomment this to run locally
# main("blah", "bleh")
