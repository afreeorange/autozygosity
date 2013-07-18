import os
import re
from datetime import datetime

from flask import Flask, render_template, make_response, send_from_directory, request, session, redirect, url_for, abort, flash, send_file
from autozygosity import app, vcf_uploads
from models import job, job_form, token_form
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


@app.route('/download/<token:token>/input', methods=['GET'])
def download_input(token):
	try:
		submission = job.objects(token__contains = token.lower())[0]
	except Exception, e:
		abort(404)
	else:
		return send_file(submission.input_vcf_path, as_attachment=True)


@app.route('/download/<token:token>/output', methods=['GET'])
@check_download
def download_output(token):
	return send_file(get_submission(token).output_zip_path, as_attachment=True)


@app.route('/download/<token:token>/output/vcf', methods=['GET'])
@check_download
def download_output_vcf(token):
	return send_file(get_submission(token).output_vcf_path, as_attachment=True)


@app.route('/download/<token:token>/output/bed', methods=['GET'])
@check_download
def download_output_bed(token):
	return send_file(get_submission(token).output_bed_path, as_attachment=True)


@app.route('/token/check', methods=['POST'])
@app.route('/token/<token:token>', methods=['GET'])
def token(token = None):
	if request.method == 'POST':
		token = request.form['token']

	try:
		submission = job.objects(token__contains = token.lower())[0]
	except Exception, e:
		abort(404)
	else:
		bed_data = []
		try:
			with open(submission.output_bed_path()) as file:
				for line in file:
					bed_data.append(tuple(line.split()))
		except Exception, e:
			pass
		return render_template("token.html", submission = submission, bed_data = bed_data)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	submission_form = job_form()

	if request.method == 'POST' and submission_form.validate():
		token = generate_token()
		submission_time = datetime.now()
		submission_folder = submission_time.strftime('%Y-%m-%dT%H:%M:%S')

		vcf_job = job(token=token, ip_address=request.remote_addr, submitted=submission_time)
		vcf_job.save()

		try:
			upload = vcf_uploads.save(storage=request.files['vcf'], folder="".join([submission_folder, "-", token]), name="input.vcf")
			return render_template("uploaded.html", token=token)
		except Exception, e:
			abort(500)

	return render_template("index.html", submission_form=submission_form, status_form=token_form())


@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static/img'),
							   'favicon.ico',
							   mimetype='image/vnd.microsoft.icon')

