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


def generate_url(data, arg_1=None, arg_2=None):

	if data == 'matchups':

		if arg_2 < 16:
			return 'http://www.espn.com/college-football/scoreboard/_/'\
			+ 'group/80/year/%s/seasontype/2/week/%s'\
			% (str(arg_1), str(arg_2))

		elif arg_2 == 16:
			return 'http://www.espn.com/college-football/scoreboard/_/'\
			+ 'group/80/year/%s/seasontype/3/week/1'\
			% (str(arg_1))

	elif data == 'gameflow':

		return 'http://www.espn.com/college-football/playbyplay?'\
		+ 'gameId=%s' % (str(arg_1))

	elif data == 'metadata':

		return 'http://www.espn.com/college-football/game?gameId=%s'\
		% (str(arg_1))