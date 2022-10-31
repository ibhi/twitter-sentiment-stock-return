"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import datetime
import tweepy
from polygon import RESTClient

# df = pd.DataFrame({
#   'first column': [1, 2, 3, 4],
#   'second column': [10, 20, 30, 40]
# })

# df
stock_names = ['AAPL', 'AMT', 'AMZN', 'APRN', 'C', 'DIS', 'FB', 'GE', 'GOOGL', 'HTZ', 'LUV', 'MSFT', 'NFLX', 'SBUX', 'TSLA']

def get_secrets(filename):
    secrets_file = open(filename, "r")
    string = secrets_file.read()
    string.split('\n')

    secrets_dict={}
    for line in string.split('\n'):
        if len(line) > 0:
            secrets_dict[line.split('=')[0]]=line.split('=')[1]
    return secrets_dict

secrets = get_secrets('secrets.txt')
client = tweepy.Client(secrets['twitter_bearer_token'])

@st.cache
def get_tweets(stock_symbol, start_date_time, end_date_time):
    query = stock_symbol + " -is:retweet lang:en"
    response = client.search_recent_tweets(query=query,max_results = 100, start_time= start_date_time, end_time = end_date_time, tweet_fields = ['created_at'])
    tweets = [tweet.text for tweet in response.data]
    date = [tweet.created_at.date() for tweet in response.data]
    tweets_df = pd.DataFrame({'text': tweets ,'date':date})
    return tweets_df

def get_max_min_datetime(selected_date):
    start_date_time = datetime.datetime.combine(selected_date, datetime.datetime.min.time())
    end_date_time = datetime.datetime.combine(selected_date, datetime.datetime.max.time())
    return (start_date_time, end_date_time)

selected_stock_name = st.selectbox(label = 'Select a stock ticker', options = stock_names)
st.write('Selected stock ticker is ', selected_stock_name)

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
selected_date = st.date_input('Select a date from last 7 days', value = yesterday, min_value = yesterday - datetime.timedelta(days=6), max_value = yesterday)
st.write('Selected date is', selected_date)



start_date_time, end_date_time = get_max_min_datetime(selected_date)
st.write('Start date is', start_date_time)
st.write('End date is', end_date_time)

tweets_df = get_tweets(selected_stock_name, start_date_time, end_date_time)
tweets_df

client = RESTClient(secrets["polygonio_api_key"])

@st.cache
def get_stock_open_close(stock_name, date):
    stock_data = {
        "date":[],
        "open":[],
        "high":[],
        "low":[],
        "close":[],
        "volume":[],
        "actual_sentiment": []
    }
    dates = [date, date + datetime.timedelta(days=1), date + datetime.timedelta(days=2)]
    for date in dates:
        response_poly = client.get_daily_open_close_agg(stock_name,date.strftime('%Y-%m-%d'))
        stock_data["date"].append(datetime.datetime.fromisoformat(response_poly.from_).date())
        stock_data["open"].append(response_poly.open)
        stock_data["high"].append(response_poly.high)
        stock_data["low"].append(response_poly.low)
        stock_data["close"].append(response_poly.close)
        stock_data["volume"].append(response_poly.volume)
        stock_data["actual_sentiment"].append('bullish' if((response_poly.open - response_poly.close) > 0) else 'bearish')
    df = pd.DataFrame(stock_data)
    return df

stock_df = get_stock_open_close(selected_stock_name, selected_date)
stock_df

merged_df = pd.merge(tweets_df, stock_df, how='inner', on='date')
merged_df