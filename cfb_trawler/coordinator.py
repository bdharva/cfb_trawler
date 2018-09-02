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


from .gameflow import *
from .matchup import *
from .metadata import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import csv


def coordinator(year, week, weeks = 1, data = 'all'):

	start_week = week
	end_week = week + weeks

	if end_week > 17:
		end_week = 17

	options = Options()
	options.add_argument('--headless')
	driver = webdriver.Chrome('/usr/local/bin/chromedriver',\
	chrome_options=options)

	for i in range(start_week, end_week):
		url = None

		if i < 16:
			url = 'http://www.espn.com/college-football/scoreboard/_/'\
			+ 'group/80/year/%s/seasontype/2/week/%s'\
			% (str(year), str(i))

		elif i == 16:
			url = 'http://www.espn.com/college-football/scoreboard/_/'
			+ 'group/80/year/%s/seasontype/3/week/1'\
			% (str(year))

		print('Trawling week ' + str(i) + ' of the ' + str(year)\
		+ ' season...')
		driver.get(url)
		print('    * Loaded ' + url)

		if data == 'matchups' or data == 'all':
			print('    * Extracting matchups')
			results = Matchup_Extractor().getResults(driver.page_source)
			print('    * Writing results')

			with open('exports/matchups_' + str(year) + '_week' +\
			str(week) + '.csv', 'w') as output:
				writer = csv.writer(output, lineterminator='\n')
				writer.writerow(['year', 'week', 'game_id',\
					'away_team', 'away_team_rank', 'away_team_record',\
					'away_team_score', 'home_team', 'home_team_rank',\
					'home_team_record', 'home_team_score'])

				for result in results:
					writer.writerow([year, week, result.game_id,\
					result.away_team.name, result.away_team.rank,\
					result.away_team.record, result.away_team.score,\
					result.home_team.name, result.home_team.rank,\
					result.home_team.record, result.home_team.score])

			print('    * Results written')

		#if data == 'metadata' or data == 'all':
			# do something
			# http://www.espn.com/college-football/game?gameId=401019470

		#if data == 'gameflow' or data == 'all':
			# do something

# # From gameflow

# if __name__ == '__main__':

# 	options = Options()
# 	options.add_argument('--headless')
# 	driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)

# 	#driver = webdriver.PhantomJS()

# 	#year = sys.argv[1]
# 	#week = sys.argv[2]
# 	game_id = 400935379
# 	# url = 'http://www.espn.com/college-football/scoreboard/_/year/%s/seasontype/2/week/%s' % (str(year), str(week))
# 	url = 'http://www.espn.com/college-football/playbyplay?gameId=%s' % (str(game_id))
# 	print(url)
# 	driver.get(url)
# 	print('Starting extractor...')
# 	results = Extractor().getResults(driver.page_source)
# 	with open('exports/drives.csv', 'w') as output:
# 		writer = csv.writer(output, lineterminator='\n')
# 		writer.writerow(['game_id','team','result','summary','home_team','home_score','away_team','away_score'])
# 		for drive in results.drives:
# 			writer.writerow([drive.game_id, drive.team, drive.result, drive.summary, drive.home_team, drive.home_score, drive.away_team, drive.away_score])
# 	with open('exports/plays.csv', 'w') as output:
# 		writer = csv.writer(output, lineterminator='\n')
# 		writer.writerow(['game_id','team','summary','description'])
# 		for play in results.plays:
# 			writer.writerow([play.game_id, play.team, play.summary, play.description])
# 	print('Completed!')