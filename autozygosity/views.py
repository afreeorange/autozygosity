import os
from datetime import datetime

from flask import Flask, render_template, make_response, send_from_directory, request, session, redirect, url_for, abort, flash
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


@app.route('/token/<token:token>', methods=['GET'])
def token(token):
	try:
		submission = job.objects(token__contains = token.lower())[0]
	except Exception, e:
		return render_template("token.html")
	else:
		bed_data = []
		with open('/Users/nikhil/Dropbox/autozygosity/uploads/2013-07-16T14:26:35-jasslem/output.bed') as file:
			for line in file:
				bed_data.append(tuple(line.split()))
		return render_template("token.html", submission = submission, bed_data = bed_data)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	submission_form = job_form()
	tokens = None

	if 'token' in session:
		tokens = session['token'].split(',')
		print tokens

	if request.method == 'POST' and submission_form.validate():
		token = upload_token()
		submission_time = datetime.now()
		submission_folder = submission_time.strftime('%Y-%m-%dT%H:%M:%S')

		vcf_job = job(token=token, ip_address=request.remote_addr, submitted=submission_time)
		vcf_job.save()

		try:
			upload = vcf_uploads.save(storage=request.files['vcf'], folder="".join([submission_folder, "-", token]), name="input.vcf")
			session['token'] = ",".join([session['token'], token])
			return render_template("uploaded.html", token=token)
		except Exception, e:
			abort(500)

	return render_template("index.html", submission_form=submission_form, status_form=token_form(), tokens=tokens)


@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static/img'),
							   'favicon.ico',
							   mimetype='image/vnd.microsoft.icon')

