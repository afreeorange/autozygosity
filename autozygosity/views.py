import os
import re
from datetime import datetime

from flask import Flask, render_template, make_response, send_from_directory, request, session, redirect, url_for, abort, flash, send_file
from autozygosity import app, vcf_uploads
from models import job, job_form, check_form
from helpers import *


# Custom error pages
@app.errorhandler(404)
def page_not_found(e):
	return render_template('error-404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
	return render_template('error-500.html'), 500


def check_download(function):
	""" 
	Decorator for download functions. When used, ensures 
	(1) a valid token, and
	(2) that the results are ready for download 
	"""
	def decorator(*args, **kwargs):
		try:
			submission = job.objects(token__contains = kwargs['token'].lower())[0]
		except IndexError, e:
			abort(404)
		else:
			try:
				with open(submission.output_zip_path): pass
			except IOError, e:
				return render_template('error-unavailable.html', token=submission.token)
	return decorator


def first_time_check():
	""" Check if this is a first-time visitor based on a session cookie """
	if 'first_time' not in session:
		session['first_time'] = True
	else:
		session['first_time'] = False
	return session['first_time']


@app.route('/download/<token:token>/input', methods=['GET'])
def download_input(token):
	try:
		submission = job.objects(token__contains = token.lower())[0]
	except Exception, e:
		abort(404)
	else:
		return send_file(submission.input_vcf_path, as_attachment=True)


@check_download
@app.route('/download/<token:token>/output', methods=['GET'])
def download_output(token):
	return send_file(get_submission(token).output_zip_path, as_attachment=True, mimetype="application/octet-stream")


@check_download
@app.route('/download/<token:token>/output/vcf', methods=['GET'])
def download_output_vcf(token):
	return send_file(get_submission(token).output_vcf_path, as_attachment=True, mimetype="text/vcf")


@check_download
@app.route('/download/<token:token>/output/bed', methods=['GET'])
def download_output_bed(token):
	return send_file(get_submission(token).output_bed_path, as_attachment=True, mimetype="text/bed")


@app.route('/token/check', methods=['POST'])
@app.route('/token/<token:token>', methods=['GET'])
def token(token = None):
	if request.method == 'POST':
		token = request.form['token']

	jobs_ahead = job.get_submitted().count() - 1

	try:
		submission = job.objects(token__contains = token.lower())[0]
	except Exception, e:
		abort(404)
	else:
		bed_data = []
		try:
			with open(submission.output_bed_path) as file:
				for line in file:
					bed_data.append(tuple(line.split()))
		except Exception, e:
			pass
		resp = make_response(render_template("token.html", submission = submission, bed_data = bed_data, jobs_ahead=jobs_ahead))
		resp.headers.add('token', token) # Need this for JQuery form plugin redirect
		return resp


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	submission_form = job_form()
	token_form = check_form()

	if request.method == 'POST' and submission_form.validate():
		token = generate_token()
		submission_time = datetime.now()
		submission_folder = submission_time.strftime('%Y-%m-%dT%H:%M:%S')

		vcf_job = job(token=token, ip_address=request.remote_addr, submitted=submission_time)
		vcf_job.save()

		try:
			upload = vcf_uploads.save(storage=request.files['vcf'], folder="".join([submission_folder, "-", token]), name="input.vcf")
		except Exception, e:
			abort(500)
		else:
			session['last_token'] = token
			return redirect("/token/" + token)

	elif request.method == 'POST' and token_form.validate():
		token(request.form['token'])

	return render_template("index.html", submission_form=submission_form, token_form=token_form)


@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static/img'),
							   'favicon.ico',
							   mimetype='image/vnd.microsoft.icon')

