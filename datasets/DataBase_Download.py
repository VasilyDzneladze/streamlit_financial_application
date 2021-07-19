import csv, os
import pandas as pd
import yfinance as yf
import time

begin = time.time()

companies = csv.reader(open("C:\\data_science_projects\\streamlit\\streamlit-dashboard-final-project\\datasets\\finviz_market.csv"))
for company in companies:

    symbol, name = company

    history_filename = f'daily/{symbol}.csv'

    f = open(history_filename, 'w')

    ticker = yf.Ticker(symbol)

    df = ticker.history(period = '1y',interval="1d")

    f.write(df.to_csv())

    f.close()


finish = time.time()

elapsed = finish - begin

print(f'Script completed in {elapsed} seconds')
