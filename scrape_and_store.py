"""
File: scrape_and_store.py
Author: Nicholas Gardner <nag6650@rit.edu>

Contains functions for scraping occupancy,
creating predictions on future occupancy,
and storing counts and predictions in a Firestore DB.
"""

import requests
import datetime
import pandas as pd
import pytz

from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import firestore

from prophet import Prophet

from constants import TIMEZONE, RIT_GYM_URL, FORMAT_VALUE_NAMES, FACILITY_COUNT_NAMES


def get_counts():
    """
    Simple scraping function. Returns the current occupancy of the three areas of the gym.
    :return: list containing [ll_count, ul_count, aq_count]
    """
    req = requests.get(RIT_GYM_URL)
    page = str(req.content, "windows-1250")
    soup = BeautifulSoup(page, 'html.parser')

    count_tags = soup.find_all("p", class_="occupancy-count")
    counts = [int(count_tag.getText()) for count_tag in count_tags[::2]]

    return counts


def store_counts(counts):
    """
    Triggers a scrape and stores the resulting counts in a firebase db
    :param counts: list containing latest scraped occupancy values
    :return: None
    """
    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    db = firestore.client()
    collection = db.collection('gym_data')

    cur_time = datetime.datetime.now()
    format_time = pd.Timestamp(cur_time).tz_localize('UTC').astimezone(pytz.timezone(TIMEZONE))

    dates = collection.document('date').get().to_dict()['entries']
    dates.append(format_time)
    collection.document('date').update({
        'entries': dates
    })

    facility_counts = []
    for idx, facility in enumerate(FORMAT_VALUE_NAMES):
        facility = "_".join(facility.lower().split(" "))

        facility_count = collection.document(facility).get().to_dict()['entries']
        facility_count.append(counts[idx])
        collection.document(facility).update({
            'entries': facility_count
        })

        facility_counts.append(facility_count)

    df = pd.DataFrame({'date': dates, FACILITY_COUNT_NAMES[0]: facility_counts[0],
                       FACILITY_COUNT_NAMES[1]: facility_counts[1], FACILITY_COUNT_NAMES[2]: facility_counts[2]})
    df['date'] = pd.to_datetime(df['date'], utc=True)
    df['date'] = df['date'].dt.tz_convert(TIMEZONE)

    predict_df = predict(df)

    collection.document('prediction').set({
        'date': pd.to_datetime(predict_df["date"].values).tolist(),
        FACILITY_COUNT_NAMES[0]: predict_df[FACILITY_COUNT_NAMES[0]].values.tolist(),
        FACILITY_COUNT_NAMES[1]: predict_df[FACILITY_COUNT_NAMES[1]].values.tolist(),
        FACILITY_COUNT_NAMES[2]: predict_df[FACILITY_COUNT_NAMES[2]].values.tolist(),
    })


def predict(df, now=None):
    """
    Predict future occupancy based on historical values
    :param df: Historical data df
    :param now: datetime.datetime.now() (localized)
    :return: Future prediction df
    """
    if now is None:
        now = datetime.datetime.now()
        tz = pytz.timezone('UTC')
        now = tz.localize(now).astimezone(pytz.timezone(TIMEZONE))

    pred_df_input = pd.melt(df, id_vars='date', value_vars=FACILITY_COUNT_NAMES)
    pred_df_input.columns = ['ds', 'facility', 'y']
    pred_df_input['ds'] = pred_df_input['ds'].dt.tz_localize(None)
    groups_by_facility = pred_df_input.groupby('facility')

    monday = now - datetime.timedelta(days=now.weekday())
    two_weeks = monday + datetime.timedelta(days=14)
    time_to_predict = two_weeks - now
    minutes_to_predict = divmod(time_to_predict.days * 86400 + time_to_predict.seconds, 60)[0]
    periods = (minutes_to_predict - (now.hour * 60)) / 30

    pred_df = pd.DataFrame()
    for idx, facility in enumerate(FACILITY_COUNT_NAMES):
        group = groups_by_facility.get_group(facility)

        model = Prophet(changepoint_prior_scale=0.05, seasonality_prior_scale=10)
        model.fit(group)
        future = model.make_future_dataframe(periods=int(periods), freq='30min', include_history=False)
        forecast = model.predict(future)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        forecast = forecast.rename(columns={'yhat': facility})

        if idx == 0:
            pred_df['ds'] = forecast['ds']
        pred_df[facility] = forecast[facility]

    pred_df = pred_df.rename(columns={'ds': 'date'})
    pred_df['date'] = pd.to_datetime(pred_df.date).dt.tz_localize('EST').dt.tz_convert(TIMEZONE)

    return pred_df
