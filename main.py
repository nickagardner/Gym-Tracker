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
FIREBASE_CREDENTIALS_FILE = "firebase_credentials.json"
PLOTLY_CREDENTIALS_FILE = "plotly_credentials.json"


def get_counts(url):
    req = requests.get(url)
    page = str(req.content, "windows-1250")
    soup = BeautifulSoup(page, 'html.parser')

    count_tags = soup.find_all("p", class_="occupancy-count")
    counts = [int(count_tag.getText()) for count_tag in count_tags[::2]]

    return counts


def store_counts(counts, firebase_cred_file):
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_cred_file)
        default_app = firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection = db.collection('gym_data_entries')

    cur_time = datetime.datetime.now()
    format_time = str(pd.Timestamp(cur_time))

    res = collection.document(format_time).set({
        'll_count': counts[0], 'ul_count': counts[1],
        'aq_count': counts[2],
    })


def render_plot(plotly_cred_file, firebase_cred_file):
    cred_file = open(plotly_cred_file)
    creds = json.load(cred_file)
    chart_studio.tools.set_credentials_file(username=creds["username"], api_key=creds["api_key"])
    chart_studio.tools.set_config_file(world_readable=True, sharing='public')

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_cred_file)
        default_app = firebase_admin.initialize_app(cred)

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

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=ll_y,
                             mode='lines+markers',
                             name='Lower Level'))
    fig.add_trace(go.Scatter(x=x, y=ul_y,
                             mode='lines+markers',
                             name='Upper Level'))
    fig.add_trace(go.Scatter(x=x, y=aq_y,
                             mode='lines+markers',
                             name='Aquatic Center'))

    # fig.update_layout(
    #     updatemenus=[
    #         dict(
    #             buttons=list([
    #                 dict(
    #                     args=[{'x': [daily_df.x], 'y': [daily_df.y]}],
    #                     label='Daily',
    #                     method='restyle'
    #                 ),
    #                 dict(
    #                     args=[{'x': [monthly_df.x], 'y': [monthly_df.y]}],
    #                     label='Monthly',
    #                     method='restyle'
    #                 )
    #             ]),
    #             direction="down",
    #             pad={"r": 10, "t": 10},
    #             showactive=True,
    #             x=0.1,
    #             xanchor="left",
    #             y=1.1,
    #             yanchor="top"
    #         ),
    #     ]
    # )
    fig.update_layout(title="RIT Recreation Facility Occupancy", xaxis_title="Date",
                      yaxis_title="Number of Occupants", legend_title="Facility Name")

    py.plot(fig, filename='RIT_gym_occupancy', auto_open=False)


def main(event_data, context):
    counts = get_counts(RIT_GYM_URL)
    store_counts(counts, FIREBASE_CREDENTIALS_FILE)
    render_plot(PLOTLY_CREDENTIALS_FILE, FIREBASE_CREDENTIALS_FILE)


# main("blah", "bleh")
