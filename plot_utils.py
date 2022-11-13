"""
File: plot_utils.py
Author: Nicholas Gardner <nag6650@rit.edu>

Utility functions for Heroku Plotly Dash Flask app plotting gym occpancy.
Contains functions for querying data from the DB, as well as
returning dataframes in the right time scale based on the user's request.
"""

import json
import os
import pandas as pd
import pytz
import datetime

import firebase_admin
from firebase_admin import credentials, firestore

from constants import FORMAT_VALUE_NAMES, FACILITY_COUNT_NAMES, TIMEZONE


def query_db():
    """
    Query firebase db for gym occupancy information
    Returns: dataframe containing occupancy information
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(json.loads(os.environ['FIREBASE_CREDENTIALS']))
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection = db.collection('gym_data')

    dates = collection.document('date').get().to_dict()['entries']
    x = dates
    columns = []
    for facility in FORMAT_VALUE_NAMES:
        facility = "_".join(facility.lower().split(" "))
        column = collection.document(facility).get().to_dict()['entries']
        columns.append(column)

    df = pd.DataFrame({'date': x, FACILITY_COUNT_NAMES[0]: columns[0], FACILITY_COUNT_NAMES[1]: columns[1],
                       FACILITY_COUNT_NAMES[2]: columns[2]})
    df['date'] = df['date'].dt.tz_convert(TIMEZONE)

    prediction = collection.document('prediction').get().to_dict()
    pred_df = pd.DataFrame({'date': prediction['date'], FACILITY_COUNT_NAMES[0]: prediction[FACILITY_COUNT_NAMES[0]],
                            FACILITY_COUNT_NAMES[1]: prediction[FACILITY_COUNT_NAMES[1]],
                            FACILITY_COUNT_NAMES[2]: prediction[FACILITY_COUNT_NAMES[2]]})
    pred_df['date'] = pred_df['date'].dt.tz_convert(TIMEZONE)

    return df, pred_df


def get_daily(df, pred_df, now=None):
    """
    Get daily focused dataframe
    Args:
        df: full dataframe
        now: day to focus on

    Returns:
        Day-focused dataframe

    """
    if now is None:
        now = datetime.datetime.now()
        tz = pytz.timezone('UTC')
        now = tz.localize(now).astimezone(pytz.timezone(TIMEZONE))
    today_begin = pd.Timestamp(tz=pytz.timezone(TIMEZONE), year=now.year,
                               month=now.month, day=now.day)

    tomorrow_date = now + datetime.timedelta(days=1, hours=1, minutes=1)
    tomorrow_begin = pd.Timestamp(tz=pytz.timezone(TIMEZONE), year=tomorrow_date.year,
                                  month=tomorrow_date.month, day=tomorrow_date.day, hour=0, minute=5)

    df_daily = df[(df['date'] >= today_begin) & (df['date'] <= tomorrow_begin)]
    pred_df_daily = pred_df[(pred_df['date'] >= now) & (pred_df['date'] <= tomorrow_begin)]

    return df_daily, pred_df_daily, today_begin, tomorrow_begin


def get_weekly(df, pred_df, now=None):
    """
    Get weekly averaged dataframe
    Args:
        df: full dataframe
        now: day to focus on

    Returns:
        Weekly averaged dataframe
    """
    if now is None:
        now = datetime.datetime.now()
        tz = pytz.timezone('UTC')
        now = tz.localize(now).astimezone(pytz.timezone(TIMEZONE))

    monday = now - datetime.timedelta(days=now.weekday())
    week_begin = pd.Timestamp(tz=pytz.timezone(TIMEZONE), year=monday.year,
                              month=monday.month, day=monday.day)
    next_monday = monday + datetime.timedelta(days=7, hours=1, minutes=1)
    week_end = pd.Timestamp(tz=pytz.timezone(TIMEZONE), year=next_monday.year,
                            month=next_monday.month, day=next_monday.day, hour=0, minute=5)
    df_weekly = df[(df['date'] >= week_begin) & (df['date'] <= week_end)]
    pred_df_weekly = pred_df[(pred_df['date'] >= week_begin) & (pred_df['date'] <= week_end)]
    df_weekly = df_weekly.set_index('date').resample('12h').mean(numeric_only=True).reset_index()
    pred_df_weekly = pred_df_weekly.set_index('date').resample('12h').mean(numeric_only=True).reset_index()

    return df_weekly, pred_df_weekly, week_begin, week_end
