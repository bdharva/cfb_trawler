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
import copy
import re


class Drive:


	def __init__(self, team='', result='', summary='', home_team='',\
	home_score='', away_team='', away_score=''):
		self.team = team
		self.result = result
		self.summary = summary
		self.home_team = home_team
		self.home_score = home_score
		self.away_team = away_team
		self.away_score = away_score


class Play:

	
	def __init__(self, team='', summary='', description=''):
		self.team = team
		self.summary = summary
		self.description = description


class Gameflow:


	def __init__(self, game_id='', drives=[], plays=[]):
		self.game_id = game_id
		self.drives = drives
		self.plays = plays


class Gameflow_Extractor(HTMLParser):


	def reset(self):
		HTMLParser.reset(self)
		self.in_plays = False
		self.in_drives = False
		self.in_header = False
		self.in_headline = False
		self.in_drive_details = False
		self.in_drive = False
		self.in_home = False
		self.in_away = False
		self.in_name = False
		self.in_score = False
		self.in_play = False
		self.in_play_summary = False
		self.in_play_description = False
		self.game = Gameflow()
		self.play = Play()
		self.drive = Drive()
		self.active_team = ''
		self.pattern = '.*?gameId=(.*)'


	def handle_starttag(self, tag, attrs):

		if tag == 'article':
			if ('class', 'sub-module play-by-play') in attrs:
				self.in_plays = True

		elif tag == 'a':

			if ('name', '&lpos=ncf:game:post:subnav:gamecast')\
			in attrs and self.in_information:

				for key, value in attrs:

					if key == 'href':
						self.game.game_id =\
						re.search(self.pattern, value).group(1)

		elif tag == 'div':

			if ('id', 'gamepackage-drives-wrap') in attrs\
			and self.in_plays:
				self.in_drives = True

			elif ('class', 'accordion-header') in attrs\
			and self.in_drives:
				self.in_header = True

		elif tag == 'span':

			if ('class', 'headline') in attrs and self.in_header:
				self.in_headline = True

			elif ('class', 'drive-details') in attrs\
			and self.in_header:
				self.in_drive_details = True

			elif ('class', 'home') in attrs and self.in_header:
				self.in_home = True

			elif ('class', 'away') in attrs and self.in_header:
				self.in_away = True

			elif ('class', 'team-name') in attrs\
			and (self.in_home or self.in_away):
				self.in_name = True

			elif ('class', 'team-score') in attrs\
			and (self.in_home or self.in_away):
				self.in_score = True

			elif ('class', 'post-play') in attrs and self.in_play:
				self.in_play_description = True

		elif tag == 'ul':

			if ('class', 'drive-list') in attrs and self.in_drives:
				self.in_drive = True

		elif tag == 'li':

			if self.in_drive:
				self.in_play = True

		elif tag == 'h3':

			if self.in_play:
				self.in_play_summary = True

		elif tag == 'img':

			if ('class', 'team-logo') in attrs and self.in_header:

				for key, value in attrs:

					if key == 'src':
						self.active_team = value.strip()

	def handle_data(self, data):

		if self.in_headline:
			self.drive.result = data.strip()
			self.in_headline = False

		elif self.in_drive_details:
			self.drive.summary = data.strip()
			self.in_drive_details = False

		elif self.in_home:

			if self.in_name:
				self.drive.home_team = data.strip()
				self.in_name = False

			elif self.in_score:
				self.drive.home_score = data.strip()
				self.in_score = False
				self.in_home = False

		elif self.in_away:

			if self.in_name:
				self.drive.away_team = data.strip()
				self.in_name = False

			elif self.in_score:
				self.drive.away_score = data.strip()
				self.games.drives.append(copy.deepcopy(self.drive))
				self.in_away = False
				self.in_header = False
				self.drive = Drive()

		elif self.in_play_summary:
			self.play.summary = data.strip()
			self.in_play_summary = False

		elif self.in_play_description:
			self.play.description = data.strip()
			self.play.team = self.active_team
			self.game.plays.append(copy.deepcopy(self.play))
			self.in_play_description = False
			self.in_play = False
			self.play = Play()

	def handle_endtag(self, tag):

		if tag == 'article' and self.in_plays:
			self.in_plays = False
			self.in_drives = False
			self.in_header = False
			self.in_headline = False
			self.in_drive_details = False
			self.in_drive = False
			self.in_home = False
			self.in_away = False
			self.in_name = False
			self.in_score = False
			self.in_play = False
			self.in_play_summary = False
			self.in_play_description = False
			self.play = Play()
			self.drive = Drive()
			self.active_team = ''

	def getResults(self, url):

		self.reset()
		self.feed(url)
		return self.game