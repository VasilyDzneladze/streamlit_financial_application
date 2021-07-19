import os
import redis
import tweepy
import numpy as np
import pandas as pd
import talib as ta
import yfinance as yf
import streamlit as st
import requests, json
import psycopg2, psycopg2.extras
import plotly.graph_objects as go
from iex import IEXStock
from helper import format_number
from patterns import candlestick_patterns
from datetime import datetime, timedelta

connection = psycopg2.connect(host=os.environ.get('DB_HOST'), database=os.environ.get('DB_NAME'), user=os.environ.get('DB_USER'), password=os.environ.get('DB_PASSWORD'))
cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

st.sidebar.title("Options")

option = st.sidebar.selectbox('Which Dashboard?',
	('Twitter', 'Stocktwits', 'WallStreetBets','IEX_Cloud','CandleSticks', 'Screeners', 'Prices and Charts'),0)


st.header(option)


if option == 'IEX_Cloud':

	redis_client = redis.Redis(host='localhost', port = 6379, db=0)

	symbol = st.sidebar.text_input("Symbol", value = 'MSFT')

	stock = IEXStock(os.environ.get('IEX_API_SECRET'), symbol)

	screen = st.sidebar.selectbox("View",('Overview', 'Statistics', 'Financials', 'Peer Group', 'News'),0)

	st.title(screen)

	if screen == 'Overview':
		logo_key = f'{symbol}_logo'
		logo = redis_client.get(logo_key)
		
		if logo is None:
			logo = stock.get_logo()
			redis_client.set(logo_key, json.dumps(logo))
		else:
			logo = json.loads(logo)

		company_key = f'{symbol}_company_info'
		company_info = redis_client.get(company_key)

		if company_info is None:
			company_info = stock.get_company_info()
			redis_client.set(company_key, json.dumps(company_info))
			redis_client.expire(company_key, timedelta(hours=24))
		else:
			company_info = json.loads(company_info)

		col1, col2 = st.beta_columns([0.7,4])

		with col1:
			st.image(logo['url'])

		with col2:
			st.subheader(company_info['symbol'])
			st.subheader(company_info['companyName'])
			st.write(company_info['industry'])
			st.write(company_info['website'])
			st.write(company_info['description'])
			st.write("Company CEO"+" "+company_info['CEO'])
			st.write("Number of company employees"+" "+str(company_info['employees']))
				
	if screen == 'Statistics':
			advanced_stats_keys = f'{symbol}_advanced_stats' 
			advanced_stats = redis_client.get(advanced_stats_keys)

			if advanced_stats is None:
				advanced_stats = stock.get_advanced_stats()
				redis_client.set(advanced_stats_keys, json.dumps(advanced_stats))
				redis_client.expire(advanced_stats_keys, timedelta(hours=24))
			else:
				advanced_stats = json.loads(advanced_stats)
				
			key_stats_keys = f'{symbol}_key_stats' 
			key_stats = redis_client.get(key_stats_keys)

			if key_stats is None:
				key_stats = stock.get_key_stats()
				redis_client.set(key_stats_keys, json.dumps(key_stats))
				redis_client.expire(key_stats_keys, timedelta(hours=24))
			else:
				key_stats = json.loads(key_stats)
			

			col1, col2= st.beta_columns([3,3])

			with col1:
				try:
					st.write("Total Cash" + " " + str(format_number(advanced_stats['totalCash'])))
					st.write("Current Debt" + " " + str(format_number(advanced_stats['currentDebt'])))
					st.write("Revenue" + " " + str(format_number(advanced_stats['revenue'])))
					st.write("Gross Profit" + " " + str(format_number(advanced_stats['grossProfit'])))
					st.write("Total Revenue" + " " + str(format_number(advanced_stats['totalRevenue'])))
					st.write("Revenue per share" + " " + str(format_number(advanced_stats['revenuePerShare'])))
					st.write("Revenue per employee" + " " + str(format_number(advanced_stats['revenuePerEmployee'])))
					st.write("Debt to equity" + " " + str(round(advanced_stats['debtToEquity'],3)))
					st.write("Profit Margin" + " " + str(round(advanced_stats['profitMargin'],3)))
					st.write("EV to revenue" + " " + str(advanced_stats['enterpriseValueToRevenue']))
					st.write("Price to Sales" + " " + str(advanced_stats['priceToSales']))
					st.write("Price to Book" + " " + str(advanced_stats['priceToBook']))
					st.write("Forward PE" + " " + str(advanced_stats['forwardPERatio']))
					st.write("PEG PE" + " " + str(round(advanced_stats['pegRatio'],3)))
					st.write("Put/Call Ratio" + " " + str(round(advanced_stats['putCallRatio'],3)))
				except:
					st.write(f"There is no statistical data for {symbol}")

			with col2:
				try:
					st.write("Enterprise Value" + " " + str(format_number(advanced_stats['enterpriseValue'])))
					st.write("Market Cap" + " " + str(format_number(key_stats['marketcap'])))
					st.write("Beta" + " " + str(key_stats['beta']))
					st.write("week52high" + " " + str(key_stats['week52high']))
					st.write("week52low" + " " + str(key_stats['week52low']))
					st.write("week52low" + " " + str(key_stats['week52low']))
					st.write("week52change" + " " + str(round(key_stats['week52change'],3)))
					st.write("Shares Outstanding" + " " + str(format_number(key_stats['sharesOutstanding'])))
					st.write("avg10Volume" + " " + str(key_stats['avg10Volume']))
					st.write("avg30Volume" + " " + str(key_stats['avg30Volume']))
					st.write("day50MovingAvg" + " " + str(round(key_stats['day50MovingAvg'],3)))
					st.write("day200MovingAvg" + " " + str(round(key_stats['day200MovingAvg'],3)))
					st.write("ytdChangePercent" + " " + str(round(key_stats['ytdChangePercent'],3)))
					st.write("month1ChangePercent" + " " + str(round(key_stats['month1ChangePercent'],3)))
					st.write("month3ChangePercent" + " " + str(round(key_stats['month3ChangePercent'],3)))
				except:
					st.write(f"There is no statistical data for {symbol}")

	if screen == 'Financials':
		financials_keys = f'{symbol}_company_financials'
		financials = redis_client.get(financials_keys)

		if financials is None:
			financials = stock.get_financials()
			redis_client.set(financials_keys, json.dumps(financials))
			redis_client.expire(financials_keys, timedelta(hours=24))
		else:
			financials = json.loads(financials)
		
		
		col1, col2 = st.beta_columns([3,3])

		
		with col1:
			try:
				st.write("EBITDA" + " " + str(format_number(financials['financials'][0]['EBITDA'])))
				st.write("accountsPayable" + " " + str(format_number(financials['financials'][0]['accountsPayable'])))
				st.write("capitalSurplus" + " " + str(financials['financials'][0]['capitalSurplus']))
				st.write("cashChange" + " " + str(format_number(financials['financials'][0]['cashChange'])))
				st.write("cashFlow" + " " + str(format_number(financials['financials'][0]['cashFlow'])))
				st.write("cashFlowFinancing" + " " + str(format_number(financials['financials'][0]['cashFlowFinancing'])))
				st.write("changesInInventories" + " " + str(format_number(financials['financials'][0]['changesInInventories'])))
				st.write("changesInReceivables" + " " + str(format_number(financials['financials'][0]['changesInReceivables'])))
				st.write("costOfRevenue" + " " + str(format_number(financials['financials'][0]['costOfRevenue'])))
				st.write("currentAssets" + " " + str(format_number(financials['financials'][0]['currentAssets'])))
				st.write("currentCash" + " " + str(format_number(financials['financials'][0]['accountsPayable'])))
				st.write("currentDebt" + " " + str(format_number(financials['financials'][0]['currentDebt'])))
				st.write("currentLongTermDebt" + " " + str(format_number(financials['financials'][0]['currentLongTermDebt'])))
				st.write("depreciation" + " " + str(format_number(financials['financials'][0]['depreciation'])))
				st.write("dividendsPaid" + " " + str(financials['financials'][0]['dividendsPaid']))
				st.write("ebit" + " " + str(format_number(financials['financials'][0]['ebit'])))
				st.write("goodwill" + " " + str(format_number(financials['financials'][0]['goodwill'])))
				st.write("grossProfit" + " " + str(format_number(financials['financials'][0]['grossProfit'])))
				st.write("incomeTax" + " " + str(format_number(financials['financials'][0]['incomeTax'])))
				st.write("intangibleAssets" + " " + str(format_number(financials['financials'][0]['intangibleAssets'])))
			except:
				st.write(f"There is no financial data for {symbol}")
		with col2:
			try:
				st.write("interestIncome" + " " + str(format_number(financials['financials'][0]['interestIncome'])))
				st.write("inventory" + " " + str(format_number(financials['financials'][0]['inventory'])))
				st.write("investments" + " " + str(financials['financials'][0]['investments']))
				st.write("longTermDebt" + " " + str(format_number(financials['financials'][0]['longTermDebt'])))
				st.write("longTermInvestments" + " " + str(format_number(financials['financials'][0]['longTermInvestments'])))
				st.write("netIncome" + " " + str(format_number(financials['financials'][0]['netIncome'])))
				st.write("operatingExpense" + " " + str(format_number(financials['financials'][0]['operatingExpense'])))
				st.write("operatingIncome" + " " + str(format_number(financials['financials'][0]['operatingIncome'])))
				st.write("receivables" + " " + str(format_number(financials['financials'][0]['receivables'])))
				st.write("totalAssets" + " " + str(format_number(financials['financials'][0]['totalAssets'])))
				st.write("interestIncome" + " " + str(format_number(financials['financials'][0]['interestIncome'])))
				st.write("totalCash" + " " + str(format_number(financials['financials'][0]['totalCash'])))
				st.write("totalDebt" + " " + str(format_number(financials['financials'][0]['totalDebt'])))
				st.write("totalInvestingCashFlows" + " " + str(format_number(financials['financials'][0]['totalInvestingCashFlows'])))
				st.write("totalLiabilities" + " " + str(format_number(financials['financials'][0]['totalLiabilities'])))
				st.write("totalRevenue" + " " + str(format_number(financials['financials'][0]['totalRevenue'])))
				st.write("treasuryStock" + " " + str(format_number(financials['financials'][0]['treasuryStock'])))
			except:
				st.write(f"There is no financial data for {symbol}")
		
	if screen == 'Peer Group':
		logo_key = f'{symbol}_logo'
		logo = redis_client.get(logo_key)
		
		if logo is None:
			logo = stock.get_logo()
			redis_client.set(logo_key, json.dumps(logo))
		else:
			logo = json.loads(logo)

		symbol_keys = f'{symbol}_company_financials'
		financials = redis_client.get(symbol_keys)

		if financials is None:
			financials = stock.get_financials()
			redis_client.set(symbol_keys, json.dumps(financials))
			redis_client.expire(symbol_keys, timedelta(hours=24))
		else:
			financials = json.loads(financials)
		

		peers_keys = f'{symbol}_company_peers'
		peers = redis_client.get(peers_keys)

		if peers is None:
			peers = stock.get_peers()
			redis_client.set(peers_keys, json.dumps(peers))
			redis_client.expire(peers_keys, timedelta(hours=24))
		else:
			peers = json.loads(peers)


		st.image(logo['url'])
		st.write(financials['symbol'])
		st.write(peers)


	if screen == 'News':
	    news_key = f"{symbol}_news"
	    news = redis_client.get(news_key)

	    if news is not None:
	        news = json.loads(news)
	    else:
	        news = stock.get_news()
	        redis_client.set(news_key, json.dumps(news))

	    for article in news:
	        st.subheader(article['headline'])
	        dt = datetime.utcfromtimestamp(article['datetime']/1000).isoformat()
	        st.write(f"Posted by {article['source']} at {dt}")
	        st.write(article['url'])
	        st.write(article['summary'])
	        st.image(article['image'])


TWITTER_USERNAMES = ('mwebster1971', 'monsterstocks1', 'Upticken', 'RossHaber',
	'1charts6', 'JPoco722', 'BlogJulianKomar', 'johnscharts', 'RayTL_',
	'gmorton512', '801010athlete', 'KGD_Investor', 'EBoboch', 'irusha',
	'SaitoChung', 'IBD_CGessel', 'mardermarket', 'LindaRaschke',
	'traderstewie',	'the_chart_life', 'canuck2usa', 'sunrisetrader',
	'tmltrader','InvezzPortal',	'priceinaction', 'canslim_', 'williamoneilco',
	'irusha','RedDogT3','SJosephBurns', 'KermitCapital', 'TraderLion_',
	'BobbyAxelrod_','JonahLupton', 'ControltheTrade', 'SahilBloom',
	'LiebermanAustin', 'RampCapitalLLC', 'Stocktwits', 'IBDinvestors',
	'investing_city', 'richard_chu97', 'alphacharts365', 'Trader_mcaruso',
	'CubbieBears', 'jfahmy', 'Upticken', 'StockDweebs', 'TraderAmogh',
	'RayTL_', 'ThweisSXFX','Scot1andT', 'PatrickWalker56', 'duckman1717',
	'PatternProfits', 'MartyChargin', 'ModDarvasBox', 'DeniseKShull',
	'TradingComposur', 'LoneStockTrader', 'monsterstocks1', 'LeifSoreide',
	'BlogJulianKomar','JackCorsellis', 'PartTimeLarry', 'ChartBreakouts',
	'mwebster1971','Tischendorf', 'RichardMoglen', 'markminervini',
	'TMLTrader', 'WishingWealth')

TWITTER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
TWITTER_CONSUMER = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')

if option == 'Twitter':
	auth = tweepy.AppAuthHandler(TWITTER_CONSUMER, TWITTER_SECRET)
	api = tweepy.API(auth)
		
	for username in TWITTER_USERNAMES:
		user = api.get_user(username)
		tweets = api.user_timeline(username)

		st.subheader(username)
		st.image(user.profile_image_url)
		
		for tweet in tweets:
			if '$' in tweet.text:
				words = tweet.text.split(' ')
				for word in words:
					if word.startswith('$') and word[1:].isalpha():
						symbol = word[1:]
						st.write(symbol)
						st.write(tweet.text)
						st.image(f'https://finviz.com/chart.ashx?t={symbol}')


if option == 'Stocktwits':
	symbol = st.sidebar.text_input("Symbol", value='PLTR', max_chars=5)
	
	r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")
	data = r.json()	
	
	for messsage in data['messages']:
		st.image(messsage['user']["avatar_url"])
		st.write(messsage['user']["name"])
		st.write(messsage["created_at"])
		st.write(messsage['source']["title"])
		st.write(messsage["body"])
		st.write(messsage['source']["url"])


if option == 'WallStreetBets':
    num_days = st.sidebar.slider('Number of days', 1, 30, 3)

    cursor.execute("""
        SELECT COUNT(*) AS num_mentions, symbol
        FROM mention JOIN stock ON stock.id = mention.stock_id
        WHERE date(dt) > current_date - interval '%s day'
        GROUP BY stock_id, symbol
        HAVING COUNT(symbol) > 10
        ORDER BY num_mentions DESC
    """, (num_days,))

    counts = cursor.fetchall()
    for count in counts:
        st.write(count)
    
    cursor.execute("""
        SELECT symbol, message, url, dt
        FROM mention JOIN stock ON stock.id = mention.stock_id
        ORDER BY dt DESC
        LIMIT 100
    """)

    mentions = cursor.fetchall()
    for mention in mentions:
        st.text(mention['dt'])
        st.text(mention['symbol'])
        st.text(mention['message'])
        st.write(mention['url'])
        # st.text(mention['username'])

    rows = cursor.fetchall()

    st.write(rows)


if option == 'CandleSticks':

	st.sidebar.title("Choose from candlestick patterns")

	option = st.sidebar.selectbox('View',('Three Advancing White Soldiers',
			'Dragonfly Doji', 'Engulfing Pattern', 'Hammer', 'Morning Star'),0)


	if option == 'Engulfing Pattern':

		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			try:
				engulfing = ta.CDLENGULFING(df['Open'], df['High'], df['Low'], df['Close'])
				last = engulfing.tail(1).values[0]
				if last > 0:
					st.write(f'{symbol} is bullish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				elif last < 0:
					st.write(f'{symbol} is bearish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				else:
					pass

			except:
				pass

	if option == 'Three Advancing White Soldiers':
		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			try:
				three_white_soldiers = ta.CDL3WHITESOLDIERS(df['Open'], df['High'], df['Low'], df['Close'])
				last = three_white_soldiers.tail(1).values[0]
				if last > 0:
					st.write(f'{symbol} is bullish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				elif last < 0:
					st.write(f'{symbol} is bearish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				else:
					pass

			except:
				pass

	if option == 'Dragonfly Doji':
		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			try:
				dragon_doji = ta.CDLDRAGONFLYDOJI(df['Open'], df['High'], df['Low'], df['Close'])
				last = dragon_doji.tail(1).values[0]
				if last > 0:
					st.write(f'{symbol} is bullish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				elif last < 0:
					st.write(f'{symbol} is bearish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				else:
					pass

			except:
				pass

	if option == 'Hammer':

		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			try:
				hammer = ta.CDLHAMMER(df['Open'], df['High'], df['Low'], df['Close'])
				last = hammer.tail(1).values[0]
				if last > 0:
					st.write(f'{symbol} is bullish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				elif last < 0:
					st.write(f'{symbol} is bearish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				else:
					pass

			except:
				pass


	if option == 'Morning Star':

		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			try:
				morning_star = ta.CDLMORNINGSTAR(df['Open'], df['High'], df['Low'], df['Close'])
				last = morning_star.tail(1).values[0]
				if last > 0:
					st.write(f'{symbol} is bullish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				elif last < 0:
					st.write(f'{symbol} is bearish')
					st.image(f'https://finviz.com/chart.ashx?t={symbol}')
				else:
					pass

			except:
				pass


if option == 'Screeners':
	st.sidebar.title("Choose from Screener")

	option = st.sidebar.selectbox("Strategies", ('Consolidating','Breaking','Volume increase','Upside Momentum', 'Mark Minervini'), 1)

	if option == 'Consolidating':

		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			def consolidating(df, percentage = 2.5):
				recent_candlesticks = df[-20:]

				max_close = recent_candlesticks['Close'].max()
				min_close = recent_candlesticks['Close'].min()

				threshold = 1 - (percentage/100)
				if min_close > (max_close * threshold):
					return True
				return False

			if consolidating(df):
				st.write(f"{symbol} is consalidating")
				st.image(f'https://finviz.com/chart.ashx?t={symbol}')


	if option == 'Breaking':

		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			def consolidating(df, percentage = 5):
				recent_candlesticks = df[-20:]
				max_close = recent_candlesticks['Close'].max()
				min_close = recent_candlesticks['Close'].min()
				threshold = 1 - (percentage/100)
				if min_close > (max_close * threshold):
					return True
				return False

			def breaking_out(df):
				last_close = df[-1:]['Close'].values[0]

				if consolidating(df[:-1],5):
					recent_closes = df[-20:-1]
					if last_close > recent_closes['Close'].max():
						return True
					return False

			if breaking_out(df):
				st.write(f"{symbol} breaking out")
				st.image(f'https://finviz.com/chart.ashx?t={symbol}')


	if option == 'Volume increase':

		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			def volume_increased(df):
				last_volume = df[-1:]['Volume'].values[0]
				average_volume = df[-20:]['Volume'].mean()

				if last_volume > (average_volume *4):
					return True
				return False

			if volume_increased(df):
				st.write(f"{symbol} breaking out")
				st.image(f'https://finviz.com/chart.ashx?t={symbol}')

	if option == 'Upside Momentum':

		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			RSI = ta.RSI(df['Close'], timeperiod=14)
			RSI_today = RSI[-1:].values[0]
			# print(RSI_today)
			ShortEMA = df.Close.ewm(span=12, adjust=False).mean()
			LongEMA = df.Close.ewm(span=26, adjust=False).mean()
			MACD = ShortEMA - LongEMA
			signal = MACD.ewm(span=9, adjust=False).mean()

			today_ShortEMA = ShortEMA[-1:].values[0]
			today_LongEMA = LongEMA[-1:].values[0]
			today_MACD = today_ShortEMA-today_LongEMA
			today_signal=signal[-1:].values[0]

			df_L= df['Low'].rolling(window=14).mean()
			df_H = df['High'].rolling(window=14).mean()
			K = 100*((df['Close'] - df_L) / (df_H - df_L) )
			D = K.rolling(window=3).mean()
			today_K = K[-1:].values[0]
			today_D = D[-1:].values[0]

			if today_ShortEMA > today_LongEMA and today_MACD > today_signal  and RSI_today > 50 and today_K > today_D:
				st.write(f"{symbol} in Upside Momentum")
				st.image(f'https://finviz.com/chart.ashx?t={symbol}')


	if option == 'Mark Minervini':

		datafiles = os.listdir('datasets/daily')
		for filename in datafiles:
			df = pd.read_csv(f'datasets/daily/{filename}')
			symbol = filename.split('.')[0]

			currentClose = df[-1:]['Close'].values[0]
			df['sma_50'] = ta.MA(df['Close'], timeperiod=50, matype=0)
			df['sma_150'] = ta.MA(df['Close'], timeperiod=150, matype=0)
			df['sma_200'] = ta.MA(df['Close'], timeperiod=200, matype=0)
			df['low_of_52week'] = min(df['Close'][-252:])
			df['high_of_52week'] = max(df['Close'][-252:])

			sma_50 = df['sma_50'][-1:].values[0]
			sma_150 = df['sma_150'][-1:].values[0]
			sma_200 = df['sma_200'][-1:].values[0]
			wh_52 = df['high_of_52week'][-1:].values[0]
			wl_52 = df['low_of_52week'][-1:].values[0]

			try:
				sma_200_past_20 = df['sma_200'][-20].values[0]
			except Exception:
				sma_200_past_20 = 0

			if currentClose > sma_50 and currentClose > sma_150 and currentClose > sma_200:
				cond_1 = True
			else:
				cond_1 = False

			if sma_150 > sma_200:
				cond_2 = True
			else:
				cond_2 = False

			if currentClose > wl_52 * 1.3 and currentClose > wh_52 * 0.8:
				cond_3 = True
			else:
				cond_3 = False

			if sma_200 > sma_200_past_20:
				cond_4 = True
			else:
				cond_4 = False

			if cond_1 and cond_2 and cond_3 and cond_4:
				st.write(f"{symbol} in Minervini list")
				st.image(f'https://finviz.com/chart.ashx?t={symbol}')


if option == 'Prices and Charts':

	IEX_API_KEY = os.getenv('IEX_API_KEY')
	symbol = st.sidebar.text_input("Symbol", value='MSFT')
	start = st.sidebar.text_input("start", value='2020-01-01')
	end = st.sidebar.text_input("end", value='2021-07-16')
	url = f'https://cloud.iexapis.com/stable/stock/{symbol}/chart/2y?token={IEX_API_KEY}'
	data = requests.get(url).json()
	df = pd.DataFrame(data)
	df = df[['date', 'open', 'high', 'low',  'close', 'volume', ]]

	st.subheader(symbol.upper())

	fig = go.Figure(data=[go.Candlestick(x=df['date'],
                                     open=df['open'],
                                     high=df['high'],
                                     low=df['low'],
                                     close=df['close'])])

	st.plotly_chart(fig, use_container_width=True)

	st.write(df.tail(30))
