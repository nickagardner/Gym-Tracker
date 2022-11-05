import requests
import datetime
import pandas as pd
import pytz

from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import firestore

from prophet import Prophet


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


def store_counts(counts, timezone):
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
    format_time = pd.Timestamp(cur_time).tz_localize('UTC').astimezone(pytz.timezone(timezone))

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

    df = pd.DataFrame({'date': dates, 'll_count': lower_level, 'ul_count': upper_level, 'aq_count': aquatic_center})
    df['date'] = pd.to_datetime(df['date'], utc=True)
    df['date'] = df['date'].dt.tz_convert(timezone)

    predict_df = predict(df, timezone)

    collection.document('prediction').set({
        'date': predict_df["date"].values.tolist(),
        'facility': predict_df["facility"].values.tolist(),
        'value': predict_df["yhat"].values.tolist(),
    })


def predict(df, timezone, now=None):
    """
    Predict future occupancy based on historical values
    :param df: Historical data df
    :param timezone: Timezone to localize results in
    :param now: datetime.datetime.now() (localized)
    :return: Future prediction df
    """
    if now is None:
        now = datetime.datetime.now()
        tz = pytz.timezone('UTC')
        now = tz.localize(now).astimezone(pytz.timezone(timezone))

    pred_df_input = pd.melt(df, id_vars='date', value_vars=['ll_count', 'ul_count', 'aq_count'])
    pred_df_input.columns = ['ds', 'facility', 'y']
    pred_df_input['ds'] = pred_df_input['ds'].dt.tz_localize(None)
    groups_by_facility = pred_df_input.groupby('facility')

    monday = now - datetime.timedelta(days=now.weekday())
    two_weeks = monday + datetime.timedelta(days=14)
    time_to_predict = two_weeks - now
    minutes_to_predict = divmod(time_to_predict.days * 86400 + time_to_predict.seconds, 60)[0]
    periods = (minutes_to_predict - (now.hour * 60)) / 30

    pred_dfs = []
    for facility in ['ll_count', 'ul_count', 'aq_count']:
        group = groups_by_facility.get_group(facility)

        model = Prophet(changepoint_prior_scale=0.05, seasonality_prior_scale=10)
        model.fit(group)
        future = model.make_future_dataframe(periods=int(periods), freq='30min')
        forecast = model.predict(future)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        forecast['facility'] = group['facility'].iloc[0]

        pred_dfs.append(forecast[['ds', 'facility', 'yhat', 'yhat_upper', 'yhat_lower']])
    pred_df = pd.concat(pred_dfs)
    pred_df = pred_df.rename(columns={'ds': 'date'})
    pred_df['date'] = pd.to_datetime(pred_df.date).dt.tz_localize('EST').dt.tz_convert(timezone)

    return pred_df
