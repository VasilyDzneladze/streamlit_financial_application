import requests

class IEXStock:
	def __init__(self, token, symbol):
		self.BASE_URL = 'https://cloud.iexapis.com/stable'
		self.token = token
		self.symbol = symbol

	def get_logo(self):
		url = f'{self.BASE_URL}/stock/{self.symbol}/logo?token={self.token}'
		logo = requests.get(url).json()
		return logo


	def get_company_info(self):
		url = f'{self.BASE_URL}/stock/{self.symbol}/company?token={self.token}'
		company_info = requests.get(url).json()
		return company_info


	def get_advanced_stats(self):
		url = f'{self.BASE_URL}/stock/{self.symbol}/advanced-stats?token={self.token}'
		advanced_stats = requests.get(url).json()
		return advanced_stats

	def get_key_stats(self):
		url = f'{self.BASE_URL}/stock/{self.symbol}/stats?token={self.token}'
		key_stats = requests.get(url).json()
		return key_stats

	def get_financials(self):
		url = f'{self.BASE_URL}/stock/{self.symbol}/financials?token={self.token}'
		financials = requests.get(url).json()
		return financials

	def get_peers(self):
		url = f'{self.BASE_URL}/stock/{self.symbol}/peers?token={self.token}'
		peers = requests.get(url).json()
		return peers

	def get_news(self):
		url = f'{self.BASE_URL}/stock/{self.symbol}/news/last?token={self.token}'
		news = requests.get(url).json()
		return news