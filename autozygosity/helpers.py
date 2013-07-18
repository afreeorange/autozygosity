import string
import itertools
import random
import re
from datetime import datetime

from autozygosity import app
import models

from flask import render_template, abort
from werkzeug.routing import BaseConverter


class TokenConverter(BaseConverter):
	""" Custom Flask converter for token ID """
	def __init__(self, url_map, *items):
		super(TokenConverter, self).__init__(url_map)
		self.regex = app.config['TOKEN_REGEX']

app.url_map.converters['token'] = TokenConverter


@app.template_filter()
def jinja_filter_add_number_commas(possible_number):
	""" Jinja2 filter to format numbers """
	try:
		number = float(possible_number)
	except ValueError, e:
		return possible_number
	else:
		return str(format(number, ',.2f'))


@app.template_filter()
def jinja_filter_status_class(status):
	""" Jinja2 filter for job status CSS classes """
	return app.config['STATUS_MAP'][status]


@app.template_filter()
def jinja_filter_reverse(s):
	""" Jinja2 filter for job status CSS classes """
	return str(s)[::-1]


def get_submission(token):
	""" Returns a models.job object given a submission token """
	return models.job.objects(token__contains = token.lower())[0]


@app.template_filter()
def jinja_filter_human_timestamp(the_timestamp):
	"""
	Jinja2 filter for human-readable timestamps
	http://stackoverflow.com/a/1551394
	"""
	now = datetime.now()
	if type(the_timestamp) is int:
		diff = now - datetime.fromtimestamp(the_timestamp)
	elif isinstance(the_timestamp,datetime):
		diff = now - the_timestamp
	elif not the_timestamp:
		diff = now - now
	else:
		return the_timestamp
	second_diff = diff.seconds
	day_diff = diff.days

	if day_diff < 0:
		return ''

	if day_diff == 0:
		if second_diff < 10:
			return "just now"
		if second_diff < 60:
			return str(second_diff) + " seconds ago"
		if second_diff < 120:
			return  "a minute ago"
		if second_diff < 3600:
			return str( second_diff / 60 ) + " minutes ago"
		if second_diff < 7200:
			return "an hour ago"
		if second_diff < 86400:
			return str( second_diff / 3600 ) + " hours ago"
	if day_diff == 1:
		return "Yesterday"
	if day_diff < 7:
		return str(day_diff) + " days ago"
	if day_diff < 31:
		return str(day_diff/7) + " weeks ago"
	if day_diff < 365:
		return str(day_diff/30) + " months ago"
	return str(day_diff/365) + " years ago"


# https://github.com/greghaskins/gibberish/blob/master/gibberish.py
initial_consonants = (set(string.ascii_lowercase) - 
					  set('aeiou') -
 					  # remove those easily confused with others
					  set('qxc') |
					  # add some crunchy clusters
					  set(['bl', 'br', 'cl', 'cr', 'dr', 'fl',
						   'fr', 'gl', 'gr', 'pl', 'pr', 'sk',
						   'sl', 'sm', 'sn', 'sp', 'st', 'str',
						   'sw', 'tr']))
final_consonants = (set(string.ascii_lowercase) - 
					set('aeiou') -
					# confusable
					set('qxcsj') |
					# crunchy clusters
					set(['ct', 'ft', 'mp', 'nd', 'ng', 'nk', 'nt',
					 	 'pt', 'sk', 'sp', 'ss', 'st']))
vowels = 'aeiou'

# each syllable is consonant-vowel-consonant "pronounceable"
syllables = map(''.join, itertools.product(initial_consonants, vowels, final_consonants))


def gibberish(wordcount, wordlist=syllables):
	return random.sample(wordlist, wordcount)


def generate_token(wordcount=2, digitcount=0):
	numbermax = 10 ** digitcount
	token = ''.join(gibberish(wordcount))
	if digitcount >= 1:
			token += str(int(random.random()*numbermax))
	return token


def permute_case(input_string):
	""" 
	Return all possible case permutations for a given input string
	http://stackoverflow.com/a/6792898 
	"""
	if not input_string:
		yield ""
	else:
		first = input_string[:1]
		if first.lower() == first.upper():
			for sub_casing in permute_case(input_string[1:]):
				yield first + sub_casing
		else:
			for sub_casing in permute_case(input_string[1:]):
				yield first.lower() + sub_casing
				yield first.upper() + sub_casing
