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


class Team:


	def __init__(self, name='', rank='99', record='', score='0'):
		self.name = name
		self.rank = rank
		self.record = record
		self.score = score


class Matchup:


	def __init__(self, game_id='', home_team=Team(), away_team=Team()):
		self.gameid = game_id
		self.home_team = home_team
		self.away_team = away_team


class Matchup_Extractor(HTMLParser):


	def reset(self):
		HTMLParser.reset(self)
		self.in_scoreboard = False
		self.in_score = False
		self.in_teams = False
		self.in_away = False
		self.in_home = False
		self.in_rank = False
		self.in_name = False
		self.in_record = False
		self.in_total = False
		self.in_totalspan = False
		self.in_id_section = False
		self.games = []
		self.matchup = Matchup()
		self.pattern = '.*?gameId=(.*)'


	def handle_starttag(self, tag, attrs):

		if tag == 'div':

			if ('class', 'scoreboard-top no-tabs') in attrs:
				self.in_scoreboard = True

		elif tag == 'section':

			if ('class', 'sb-score final') in attrs\
			and self.in_scoreboard:
				self.in_score = True

			elif ('class', 'sb-actions') in attrs:
				self.in_id_section = True

		elif tag == 'a':

			if ('name', '&lpos=college-football:scoreboard:boxscore')\
			in attrs and self.in_id_section:

				for key, value in attrs:

					if key == 'href':
						self.matchup.game_id = re.search(self.pattern, value)\
						.group(1)
						self.games.append(copy.deepcopy(self.matchup))
						self.matchup = Matchup()
						self.matchup.home_team = Team()
						self.matchup.away_team = Team()

		if tag == 'tbody':
			
			if ('id', 'teams') in attrs and self.in_score:
				self.in_teams = True

		if tag == 'tr':
			
			if ('class', 'away') in attrs and self.in_teams:
				self.in_away = True
			
			elif ('class', 'home') in attrs and self.in_teams:
				self.in_home = True

		if tag == 'span':

			if ('class', 'rank') in attrs and self.in_teams:
				self.in_rank = True

			elif ('class', 'sb-team-short') in attrs and self.in_teams:
				self.in_name = True

		if tag == 'p':

			if ('class', 'record overall') in attrs and self.in_teams:
				self.in_record = True

		if tag == 'td':

			if ('class', 'total') in attrs and self.in_teams:
				self.in_total = True

		if tag == 'span':

			if self.in_total:
				self.in_totalspan = True


	def handle_data(self, data):

		if self.in_home:

			if self.in_rank:
				self.matchup.home_team.rank = data

			elif self.in_name:
				self.matchup.home_team.name = data

			elif self.in_record:
				self.matchup.home_team.record = data

			elif self.in_totalspan:
				self.matchup.home_team.score = data

		elif self.in_away:

			if self.in_rank:
				self.matchup.away_team.rank = data

			elif self.in_name:
				self.matchup.away_team.name = data

			elif self.in_record:
				self.matchup.away_team.record = data

			elif self.in_totalspan:
				self.matchup.away_team.score = data


	def handle_endtag(self, tag):

		if tag == 'section':
			
			if self.in_score:
				self.in_score = False
				
			elif self.in_id_section:
				self.in_id_section = False

		if tag == 'tbody':
			self.in_teams = False

		if tag == 'tr':
			self.in_away = False
			self.in_home = False

		if tag == 'span':
			self.in_rank = False
			self.in_name = False
			self.in_totalspan = False

		if tag == 'p':
			self.in_record = False

		if tag == 'td':
			self.in_total = False


	def getResults(self, url):

		self.reset()
		self.feed(url)
		return self.games