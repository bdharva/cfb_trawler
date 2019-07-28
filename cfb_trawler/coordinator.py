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

def progress (i, n, length = 100, fill = '█'):
	n = n + 1
	fill_length = int(length * i // n)
	bar = fill * fill_length + '-' * (length - fill_length)
	percent = ('{0:.1f}').format(100 * (i / float(n)))
	progress = '%s%% complete (%s/%s games)' % (percent, i, n)
	print('\r\t%s %s' % (bar, progress), end = '\r')

	if i == n:
		print()

def coordinator(year, week, weeks=1, data='all'):

	start_time = time.time()
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
		print('\n\tTRAWLING WEEK ' + str(i) + ' OF THE ' + str(year)\
			+ ' SEASON...')

		if data == 'matchups' or data == 'all':
			print('\n\tMATCHUPS')
			url = generate_url('matchups', year, i)
			print('\t- Loading matchups')
			driver.get(url)
			print('\t- Extracting matchups')
			results = Matchup_Extractor().getResults(driver.page_source)
			print('\t- Writing results')

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
					writer.writerow([year, i, result.game_id,\
					result.away_team.name, result.away_team.rank,\
					result.away_team.record, result.away_team.score,\
					result.home_team.name, result.home_team.rank,\
					result.home_team.record, result.home_team.score])

			print('\t- Results written')
			delay = random.randrange(10)
			time.sleep(delay)

		if data == 'metadata' or data == 'all' or data == 'testing':
			print('\n\tMETADATA\n')

			if not os.path.exists('exports/matchups/' + str(year)\
			+ '_week_' + str(i) + '.csv'):
				print('\n\t* Error: No matchups found')

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
					'network', 'town', 'zipcode', 'line', 'over_under',\
					'attendance', 'capacity'])
					progress(0, len(game_ids), length = 50)

					for i, game_id in enumerate(game_ids):
						url = generate_url('metadata', game_id)
						driver.get(url)
						result = Metadata_Extractor()\
						.getResults(driver.page_source)
						writer.writerow([result.game_id, result.venue,\
						result.date_time, result.network, result.town,\
						result.zipcode, result.line, result.over_under,\
						result.attendance, result.capacity])
						delay = random.randrange(10)
						time.sleep(delay)
						progress(i, len(game_ids), length = 50)

		if data == 'gameflow' or data == 'all':
			print('\n\tGAMEFLOW\n')
			if not os.path.exists('exports/matchups/' + str(year)\
			+ '_week_' + str(i) + '.csv'):
				print('\n\t* Error: No matchups found')

			else:
				game_ids = []

				with open('exports/matchups/' + str(year) + '_week_'\
				+ str(i) + '.csv', 'r') as infile:
					reader = csv.reader(infile, lineterminator='\n')
					next(reader)

					for row in reader:
						game_ids.append(row[2])

				progress(0, len(game_ids), length = 50)

				for i, game_id in enumerate(game_ids):
					url = generate_url('gameflow', game_id)
					driver.get(url)
					result = Gameflow_Extractor()\
					.getResults(driver.page_source)
					
					if not os.path.exists('exports/gameflow'):
						os.mkdir('exports/gameflow')

					if not os.path.exists('exports/gameflow/drives'):
						os.mkdir('exports/gameflow/drives')

					if not os.path.exists('exports/gameflow/plays'):
						os.mkdir('exports/gameflow/plays')

					with open('exports/gameflow/plays/' + str(game_id)\
					+ '.csv', 'w') as output:
						writer = csv.writer(output, lineterminator='\n')
						writer.writerow(['game_id', 'team', 'summary',\
						'description'])

						for play in result.plays:
							writer.writerow([game_id, play.team,\
							play.summary, play.description])

					with open('exports/gameflow/drives/' + str(game_id)\
					+ '.csv', 'w') as output:
						writer = csv.writer(output, lineterminator='\n')
						writer.writerow(['game_id', 'team', 'result',\
						'summary', 'away_team', 'away_score', 'home_team', 'home_score'])

						for drive in result.drives:
							writer.writerow([game_id, drive.team,\
							drive.result, drive.summary,\
							drive.away_team, drive.away_score, drive.home_team, drive.home_score])

					delay = random.randrange(10)
					time.sleep(delay)
					progress(i, len(game_ids), length = 50)

	time_elapsed = time.time() - start_time
	print('\n\tFINISHED TRAWLING ' + data.upper() + ' DATA FOR ' + str(year)\
		+ ' SEASON, WEEK', end='')

	if weeks == 1:
		print(' ' + str(start_week), end='')

	else:
		print('S ' + str(start_week) + ' TO ' + str(end_week - 1), end='')

	if time_elapsed > 3600:
		print(' IN ' + ('{0:.1f}').format(time_elapsed/3600) + ' HOURS\n')

	elif time_elapsed > 60:
		print(' IN ' + ('{0:.1f}').format(time_elapsed/60) + ' MINUTES\n')

	else:
		print(' IN ' + ('{0:.1f}').format(time_elapsed) + ' SECONDS\n')