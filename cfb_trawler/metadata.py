# MIT License

# Copyright (c) 2018 Benjamin David Harvatine

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from html.parser import HTMLParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


class Metadata:


	def __init__(self, game_id='', venue='', date_time='', network='',\
	town='', zipcode='', odds='', attendance=''):
		self.gameid = game_id
		self.venue = venue
		self.date_time = date_time
		self.network = network
		self.town = town
		self.zipcode = zipcode
		self.odds = odds
		self.attendance = attendance


class Metadata_Extracter(HTMLParser):


	def reset(self):
		HTMLParser.reset(self)
		self.in_information = False
		self.in_venue = False
		self.in_date_time = False
		self.in_network = False
		self.in_town = False
		self.in_zipcode = False
		self.in_odds_details = False
		self.in_odds = False
		self.in_attendance = False
		self.pattern = '.*?gameId=(.*)'
		self.matchup = Matchup()


	def handle_starttag(self, tag, attrs):

		if tag == 'a':

			if ('name', '&lpos=ncf:game:post:subnav:gamecast')\
			in attrs and self.in_information:

				for key, value in attrs:

					if key == 'href':
						self.matchup.game_id =\
						re.search(self.pattern, value).group(1)

		elif tag == 'article':

			if ('class', 'sub-module game-information') in attrs:
				self.in_information = True

		elif tag == 'div':

			if (('class', 'game-location') in attrs\
			or ('class', 'caption_wrapper') in attrs)\
			and self.in_information:
				self.in_venue = True

			elif ('class', 'game-date-time') in attrs\
			and self.in_information:
				self.in_date_time = True

			elif ('class', 'game-network') in attrs\
			and self.in_information:
				self.in_date_time = True

			elif ('class', 'odds-details') in attrs\
			and self.in_information:
				self.in_odds_details = True

			elif ('class', 'game-info-note capacity') in attrs\
			and self.in_information:
				self.in_attendance = True

		elif tag == 'li':

			if ('class', 'icon-font-before icon-location-solid-before')\
			and self.in_information:
				self.in_town = True

			elif self.in_odds_details:
				self.in_odds = True

		elif tag == 'span':

			if self.in_town:
				self.in_zipcode = True


	def handle_data(self, data):

		if self.in_venue:
			self.matchup.venue = data
			self.in_venue = False

		elif self.in_date_time:
			self.matchup.date_time = data
			self.in_date_time = False

		elif self.in_network:
			self.matchup.network = data
			self.in_network = False

		elif self.in_town:
			self.matchup.town = data

		elif self.in_zipcode:
			self.matchup.zipcode = data
			self.in_zipcode = False
			self.in_town = False

		elif self.in_odds:
			self.matchup.odds = data
			self.in_odds = False
			self.in_odds_details = False

		elif self.in_attendance:
			self.matchup.attendance = data
			self.in_attendance = False


	def handle_endtag(self, tag):

		if tag == 'article':
			
			if self.in_information:
				self.in_information = False


	def getResults(self, url):

		self.reset()
		self.feed(url)
		return self.matchup