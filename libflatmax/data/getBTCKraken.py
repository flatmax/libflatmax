#!/usr/bin/env python

import krakenex
import pandas as pd
from datetime import datetime, timedelta

# Initialize Kraken API client
kraken = krakenex.API()

# Define start and end timestamps
end_timestamp = int(datetime.now().timestamp())
start_timestamp = int((datetime.now() - timedelta(days=3)).timestamp())

# Fetch historical data
response = kraken.query_public('OHLC', {
    'pair': 'XBTUSD',  # Kraken's BTC/USD pair
    'interval': 1,     # 1-minute interval
    'since': start_timestamp
})

# Parse and save data if successful
if response['error'] == []:
    df = pd.DataFrame(response['result']['XXBTZUSD'], columns=[
        'time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'
    ])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    # Save to CSV
    df.to_csv("btc_last_3_days_kraken.csv")
    print("High-resolution Kraken data saved to btc_last_3_days_kraken.csv")
else:
    print("Error fetching data:", response['error'])
