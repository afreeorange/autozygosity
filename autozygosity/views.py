import os
import re
from datetime import datetime

from flask import Flask, render_template, make_response, send_from_directory, request, session, redirect, url_for, abort, flash, send_file
from autozygosity import app, vcf_uploads
from models import job, job_form, check_form
from helpers import *
import socket


@app.errorhandler(404)
def page_not_found(e):
	""" Custom 404 error page """
	return render_template('error-404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
	""" Custom 500 error page """
	return render_template('error-500.html'), 500


@app.route('/token/<token:token>/output', methods=['GET'])
@validate_download
@validate_token
def download_output(token):
	return send_file(get_submission(token).output_zip_path, as_attachment=True, attachment_filename=token + ".output.zip", mimetype="application/octet-stream")


@app.route('/token/<token:token>/output/vcf', methods=['GET'])
@validate_download
@validate_token
def download_output_vcf(token):
	return send_file(get_submission(token).output_vcf_path, as_attachment=True, attachment_filename=token + ".output.vcf",  mimetype="text/vcf")


@app.route('/token/<token:token>/output/bed', methods=['GET'])
@validate_download
@validate_token
def download_output_bed(token):
	return send_file(get_submission(token).output_bed_path, as_attachment=True, attachment_filename=token + ".output.bed",  mimetype="text/bed")


@app.route('/token/<token:token>/input', methods=['GET'])
@validate_download
@validate_token
def download_input(token):
	return send_file(get_submission(token).input_vcf_path, as_attachment=True, attachment_filename=token + ".input.vcf")


@app.route('/token/check', methods=['POST'])
@app.route('/token/<token:token>', methods=['GET'])
@validate_token
def token(token = None):
	if request.method == 'POST':
		token = request.form['token']

	bed_data = []
	submission = job.objects(token__contains = token.lower())[0]

	try:
		with open(submission.output_bed_path) as file:
			for line in file:
				bed_data.append(tuple(line.split()))
	except Exception, e:
		pass

	resp = make_response(render_template("token.html", submission = submission, bed_data = bed_data))
	resp.headers.add('token', token) # Need this for JQuery form plugin redirect
	return resp


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	submission_form = job_form()
	token_form = check_form()

	session['explain_submission'] = True

	if request.method == 'POST' and submission_form.validate():
		token = generate_token()
		submission_time = datetime.now()
		submission_folder = submission_time.strftime('%Y-%m-%dT%H:%M:%S')

		# Try to save a record of the submission
		vcf_job = job(	token=token, 
						ip_address=request.remote_addr, 
						submitted=submission_time)
		try:
			vcf_job.save()
		except Exception, e:
			abort(500)

		# Then try to save the submission itself
		try:
			upload = vcf_uploads.save(	storage=request.files['vcf'], 
										folder="".join([submission_folder, "-", token]), 
										name="input.vcf")
		except Exception, e:
			abort(500)
		else:
			session['last_token'] = token
			return redirect("/token/" + token)

	elif request.method == 'GET':
		return render_template("index.html", submission_form=submission_form, token_form=token_form)

	else:
		abort(500)


@app.route('/misc/allowed_upload_extensions')
def allowed_extensions():
	""" Returns allowed upload extensions. Used by Javascript. Overkill. """
	return "|".join(app.config['UPLOAD_FORMAT_EXTENSIONS'])


@app.route('/misc/no_explanation', methods=['GET'])
def no_explanation():
	""" Returns allowed upload extensions. Used by Javascript. Overkill. """
	session['explain_submission'] = False
	return str(session['explain_submission'])


@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static/img'),
							   'favicon.ico',
							   mimetype='image/vnd.microsoft.icon')

