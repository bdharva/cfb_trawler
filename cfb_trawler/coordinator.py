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
from .generate_url import *
from .matchup import *
from .metadata import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import os
import random
import time


def coordinator(year, week, weeks=1, data='all'):

	start_time = time.clock()
	start_week = week
	end_week = week + weeks

	if end_week > 17:
		end_week = 17

	options = Options()
	options.add_argument('--headless')
	driver = webdriver.Chrome('/usr/local/bin/chromedriver',\
	chrome_options=options)

	if not os.path.exists('exports'):
		os.mkdir('exports')

	for i in range(start_week, end_week):
		print('Trawling week ' + str(i) + ' of the ' + str(year)\
			+ ' season...')

		if data == 'matchups' or data == 'all':
			url = generate_url('matchups', year, i)
			driver.get(url)
			print('    * Loaded ' + url)
			print('    * Extracting matchups')
			results = Matchup_Extractor().getResults(driver.page_source)
			print('    * Writing results')

			if not os.path.exists('exports/matchups'):
				os.mkdir('exports/matchups')

			with open('exports/matchups/' + str(year) + '_week_'\
			+ str(i) + '.csv', 'w') as output:
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
			delay = random.randrange(10)
			print('    * Waiting ' + str(delay) + ' seconds...')
			time.sleep(delay)

		if data == 'metadata' or data == 'all' or data == 'testing':

			if not os.path.exists('exports/matchups/' + str(year)\
			+ '_week_' + str(i) + '.csv'):
				print('    * Error: No matchups found')

			else:
				game_ids = []

				with open('exports/matchups/' + str(year) + '_week_'\
				+ str(i) + '.csv', 'r') as infile:
					reader = csv.reader(infile, lineterminator='\n')
					next(reader)

					for row in reader:
						game_ids.append(row[2])

				if not os.path.exists('exports/metadata'):
					os.mkdir('exports/metadata')

				with open('exports/metadata/' + str(year) + '_week_'\
				+ str(i) + '.csv', 'w') as output:
					writer = csv.writer(output, lineterminator='\n')
					writer.writerow(['game_id', 'venue', 'date_time',\
					'network', 'town', 'zipcode', 'odds', 'attendance',\
					'capcity'])

					for game_id in game_ids:
						url = generate_url('metadata', game_id)
						driver.get(url)
						print('    * Loaded ' + url)
						print('        * Extracting matchup metadata')
						result = Metadata_Extractor()\
						.getResults(driver.page_source)
						print('        * Writing results')
						writer.writerow([result.game_id, result.venue,\
						result.date_time, result.network, result.town,\
						result.zipcode, result.odds, result.attendance,\
						result.capacity])
						delay = random.randrange(10)
						print('        * Waiting ' + str(delay)\
						+ ' seconds...')
						time.sleep(delay)

		if data == 'gameflow' or data == 'all':

			if not os.path.exists('exports/matchups/' + str(year)\
			+ '_week_' + str(i) + '.csv'):
				print('    * Error: No matchups found')

			else:
				game_ids = []

				with open('exports/matchups/' + str(year) + '_week_'\
				+ str(i) + '.csv', 'r') as infile:
					reader = csv.reader(infile, lineterminator='\n')
					next(reader)

					for row in reader:
						game_ids.append(row[2])

				for game_id in game_ids:
					url = generate_url('gameflow', game_id)
					print(url)
					driver.get(url)
					print('    * Loaded ' + url)
					print('    * Extracting gameflow')
					result = Gameflow_Extractor()\
					.getResults(driver.page_source)
					print('    * Writing results')

					if not os.path.exists('exports/gameflow'):
						os.mkdir('exports/gameflow')

					if not os.path.exists('exports/gameflow/drives'):
						os.mkdir('exports/gameflow/drives')

					if not os.path.exists('exports/gameflow/plays'):
						os.mkdir('exports/gameflow/plays')

					with open('exports/gameflow/plays/' + str(game_id)\
					+ '.csv', 'w') as output:
						writer = scv.writer(output, lineterminator='\n')
						writer.writerow(['game_id', 'team', 'summary',\
						'description'])

						for play in result.plays:
							writer.writerow([game_id, play.team,\
							play.summary, play.description])

					with open('exports/gameflow/drives/' + str(game_id)\
					+ '.csv', 'w') as output:
						writer = scv.writer(output, lineterminator='\n')
						writer.writerow(['game_id', 'team', 'result',\
						'summary', 'home_team', 'home_score',\
						'away_team', 'away_score'])

						for drive in result.drives:
							writer.writerow([game_id, drive.team,\
							drive.result, drive.summary,\
							drive.home_team, drive.home_score,\
							drive.away_team, drive.away_score])

	time_elapsed = time.clock() - start_time
	print('Finished trawling ' + data + ' data for ' + str(year)\
	+ ' season, weeks ' + str(start_week) + ' to ' + str(end_week))

	if time_elapsed > 3600:
		print('in ' + str(time_elapsed/3600) + ' hours')

	elif time_elapsed > 60:
		print('in ' + str(time_elapsed/60) + ' minutes')

	else:
		print('in ' + str(time_elapsed) + ' seconds')