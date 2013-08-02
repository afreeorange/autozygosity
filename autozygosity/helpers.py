from datetime import datetime
from functools import wraps
from socket import getfqdn
import itertools
import random
import re
import string

from autozygosity import app
import models

from flask import render_template, abort, request, session
from werkzeug.routing import BaseConverter


class TokenConverter(BaseConverter):
	""" Custom Flask converter for token ID """
	def __init__(self, url_map, *items):
		super(TokenConverter, self).__init__(url_map)
		self.regex = app.config['TOKEN_REGEX']

app.url_map.converters['token'] = TokenConverter


def validate_token(function):
	""" Decorator that checks if given token exists in database """

	# wraps solved a silly/bizzare problem where function.__name__
	# would always return the last decorated method in this file.
	# Still don't understand why that should be the case. Need to
	# read more
	# http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
	# http://www.artima.com/weblogs/viewpost.jsp?thread=240808
	@wraps(function)
	def validate_token_decorator(*args, **kwargs):

		# Token either comes from URI or POST variable.
		# Barf if neither.
		token = None
		if 'token' in kwargs:
			token = kwargs['token']
		elif 'token' in request.form:
			token = request.form['token']
		else:
			abort(500)

		# Check if valid token
		try:
			models.job.objects(token__contains = token.lower())[0]
		except IndexError, e:
			abort(404)
		else:
			return function(*args, **kwargs)

	return validate_token_decorator


def validate_download(function):
	""" Decorator that checks if a submission's files are
		available for download. Throws a 404 if the submission
		is completed but file is unavailable for whatever reason.
		Shows appropriate pages for 'completed' and 'failed'
		statuses, and "results not ready" for all others.
	"""	

	@wraps(function)
	def validate_download_decorator(*args, **kwargs):
		submission = models.job.objects(token__contains = kwargs['token'].lower())[0]

		try:
			function(*args, **kwargs)
		except Exception, e:
			print str(e)
			if submission.status == 'completed':
				abort(404)
			elif submission.status == 'failed':
				return render_template('token.html', submission=submission)
			else:
				return render_template('errors/unavailable.html', token=submission.token)
		else:
			return function(*args, **kwargs)

	return validate_download_decorator


def jinja_method_explain_submission(submission):
	""" Jinja2 method to determine whether or not to show submission explanation.
		Aimed at first-time visitors. Assume first-time visitor if the 
		'explain_submission' cookie's not set. Don't explain completed or failed
		submissions.
	"""
	if submission.status == 'completed' or submission.status == 'failed':
		return False

	try:
		return session['explain_submission']
	except Exception, e:
		return True


def jinja_method_get_hostname():
	""" Jinja2 method to get the hostname """
	return request.host_url


# http://code.activestate.com/recipes/577081-humanized-representation-of-a-number-of-bytes/
def jinja_method_max_upload_size(bytes = app.config['UPLOADED_VCF_MAX_SIZE'], precision=0):
	""" Return a humanized string representation of a number of bytes. """
	abbrevs = (
		(1<<50L, 'PB'),
		(1<<40L, 'TB'),
		(1<<30L, 'GB'),
		(1<<20L, 'MB'),
		(1<<10L, 'kB'),
		(1, 'bytes')
	)
	if bytes == 1:
		return '1 byte'
	for factor, suffix in abbrevs:
		if bytes >= factor:
			break
	return '%.*f %s' % (precision, bytes / factor, suffix)


@app.template_filter()
def jinja_filter_jobs_ahead(job_count):
	""" Return the number of jobs ahead of current submission in a grammatically correct format """
	if job_count == 0:
		stub = "are no submissions"
	elif job_count == 1:
		stub = "is one submission"
	else:
		stub = "are " + str(job_count) + " submissions"
	return stub


@app.template_filter()
def jinja_filter_add_number_commas(possible_number):
	""" Jinja2 filter to format numbers """
	try:
		number = int(possible_number)
	except ValueError, e:
		try:
			number = float(possible_number)
		except ValueError, e:
			return possible_number
		else:
			return str(format(number, ',.2f'))
	else:
		return str(format(number, ',d'))


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


@app.template_filter()
def make_comma_list(list):
	return ", ".join(list)
