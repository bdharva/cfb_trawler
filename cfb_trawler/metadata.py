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
	town='', zipcode='', line='', over_under='', attendance='', capacity=''):
		self.game_id = game_id
		self.venue = venue
		self.date_time = date_time
		self.network = network
		self.town = town
		self.zipcode = zipcode
		self.line = line
		self.over_under = over_under
		self.attendance = attendance
		self.capacity = capacity


class Metadata_Extractor(HTMLParser):


	def reset(self):
		HTMLParser.reset(self)
		self.in_information = False
		self.figure_found = False
		self.in_venue = False
		self.in_date_time = False
		self.in_network = False
		self.in_location_details = False
		self.in_town = False
		self.in_zipcode = False
		self.in_odds = False
		self.in_line = False
		self.in_over_under = False
		self.in_attendance = False
		self.in_capacity_wrapper = False
		self.in_capacity = False
		self.pattern = '.*?gameId=(.*)'
		self.network_pattern = 'Coverage: ?(.*)'
		self.attendance_pattern = 'Attendance: ?(.*)'
		self.capacity_pattern = 'Capacity: ?(.*)'
		self.over_under_pattern = 'Over/Under: ?(.*)'
		self.matchup = Metadata()


	def handle_starttag(self, tag, attrs):

		if tag == 'meta':

			if ('property', 'og:url') in attrs:

				for key, value in attrs:

					if key == 'content':
						self.matchup.game_id =\
						re.search(self.pattern, value).group(1)

		elif tag == 'article':

			for key, value in attrs:

				if (key == 'class' and ' '.join(value.split()[:2]) ==\
				'sub-module game-information'):
					self.in_information = True

		elif tag == 'figure' and self.in_information:
			self.figure_found = True

		elif tag == 'div' and self.in_information:

			for key, value in attrs:

				if (key == 'class' and value.split()[0] == 'game-field'):
					self.in_venue = True

			if ('class', 'caption-wrapper') in attrs:
				self.in_venue = True

			elif ('class', 'game-date-time') in attrs:
				self.in_date_time = True

			elif ('class', 'game-network') in attrs:
				self.in_network = True

			elif ('class', 'location-details') in attrs:
				self.in_location_details = True

			elif ('class', 'odds-details') in attrs:
				self.in_odds = True
				self.in_town = False

			elif ('class', 'game-info-note capacity') in attrs:
				
				if self.in_capacity_wrapper:
					self.in_capacity = True

				else:
					self.in_attendance = True

			elif ('class', 'attendance') in attrs:
				self.in_attendance = False
				self.in_capacity_wrapper = True

		elif tag == 'li' and self.in_information:

			if ('class', 'icon-font-before icon-location-solid-before') in attrs:
				self.in_town = True

			elif self.in_odds:

				if ('class', 'ou') in attrs:
					self.in_over_under = True

				else:
					self.in_line = True

		elif tag == 'span':

			if self.in_date_time and ('data-behavior', 'date_time') in attrs:

				for key, value in attrs:

					if key == 'data-date':
						self.matchup.date_time = value
						self.in_date_time = False

			elif self.in_town:
				self.in_zipcode = True
				self.in_town = False

			elif self.in_location_details and not self.figure_found:
				self.in_venue = True


	def handle_data(self, data):

		if self.in_venue and self.matchup.venue == '':
			self.matchup.venue = data.strip()
			self.in_venue = False

		elif self.in_network:
			self.matchup.network = \
			re.search(self.network_pattern, data.strip()).group(1)
			self.in_network = False

		elif self.in_town:
			self.matchup.town = data.strip()

		elif self.in_zipcode:
			self.matchup.zipcode = data.strip()
			self.in_zipcode = False
			self.in_town = False

		elif self.in_line:
			self.matchup.line = data.strip()
			self.in_line = False

		elif self.in_over_under:
			self.matchup.over_under =\
			re.search(self.over_under_pattern, data.strip()).group(1)
			self.in_over_under = False
			self.in_odds = False

		elif self.in_attendance and self.matchup.attendance == '':
			try:
				self.matchup.attendance = \
				re.search(self.attendance_pattern, data.strip())\
				.group(1)
			
			except:
				self.matchup.attendance = 'null'

		elif self.in_capacity:

			try:
				self.matchup.capacity = \
				re.search(self.capacity_pattern, data.strip())\
				.group(1)

			except:
				self.matchup.capacity = 'null'

			self.in_capacity = False
			self.in_capacity_wrapper = False


	def handle_endtag(self, tag):

		if tag == 'article' and self.in_information:
			self.in_information = False
			self.in_location_details = False

		elif tag == 'li' and self.in_town:
			self.in_town = False

		elif tag == 'ul':

			if self.in_odds:
				self.in_odds = False


	def getResults(self, url):

		self.reset()
		self.feed(url)
		return self.matchup