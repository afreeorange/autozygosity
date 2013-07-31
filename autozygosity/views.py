import os
import re
from datetime import datetime
from subprocess import check_call, CalledProcessError

from flask import Flask, render_template, make_response, send_from_directory, request, session, redirect, url_for, abort, flash, send_file
from autozygosity import app, vcf_uploads
from models import job, job_form, check_form
from helpers import *
import socket
from pprint import pprint


@app.errorhandler(404)
@app.route('/misc/notfound')
def page_not_found(e = None):
	""" Custom 404 error page """
	return render_template('errors/404.html'), 404


@app.errorhandler(500)
@app.route('/misc/oops')
def server_error(e = None):
	""" Custom 500 error page """
	return render_template('errors/500.html'), 500


@app.route('/token/<token:token>/log', methods=['GET'])
@validate_token
def download_log(token):
	return send_file(get_submission(token).logfile_path, as_attachment=True, attachment_filename=token + ".analysis.log", mimetype="application/octet-stream")


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
	submission = get_submission(token)
	return send_file(submission.input_vcf_path, as_attachment=True, attachment_filename=token + "." + submission.upload_name)


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

	resp = make_response(render_template("pages/token.html", submission = submission, bed_data = bed_data))
	resp.headers.add('token', token) # Need this for JQuery form plugin redirect
	return resp


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	submission_form = job_form()
	token_form = check_form()

	# Deal with first-time visitors (show token explanation)
	if 'explain_submission' not in session:
		session['explain_submission'] = True

	if request.method == 'POST' and submission_form.validate():

		token = generate_token()
		submission_time = datetime.now()
		submission_folder = "".join([app.config['UPLOADED_VCF_DEST'], submission_time.strftime('%Y-%m-%dT%H:%M:%S'), "-", token])
		extension = ""
		savename = ""
		download_script = app.config['PROJECT_PATH'] + "scripts/download_uri.sh"
		upload_log = app.config['PROJECT_PATH'] + 'logs/uploads.log'

		# Prioritize URI location over upload for confused/naughty visitors
		if request.form['uri']:
			print "Trying", request.form['uri']

			# Try to get submission upload extension
			try:
				extension = re.compile(r'^.*?[.](?P<extension>' + '|'.join(app.config['UPLOAD_FORMAT_EXTENSIONS']) + ')$').match(request.form['uri']).group('extension')
			except Exception, e:
				savename = "input.vcf" # Assume that URIs without extension are raw VCF
				extension = "vcf"
			else:
				savename = "input." + extension

			# Try downloading remote file.
			try:
				check_call(download_script + ' '
							+ ' -u ' + request.form['uri']
							+ ' -e ' + extension
							+ ' -f ' + submission_folder
							+ ' &> ' + upload_log
							, shell=True)
			except CalledProcessError, e:
				return render_template("errors/uri.html")
			else:
				# Try saving job if upload was successful
				vcf_job = job(  token=token, 
								ip_address=request.remote_addr, 
								submitted=submission_time,
								upload_name=savename,
								min_variant_quality=request.form['min_variant_quality'],
								min_quality_depth=request.form['min_quality_depth'],
								homozyg_window_size=request.form['homozyg_window_size'],
								heterozyg_calls=request.form['heterozyg_calls'])
				try:
					vcf_job.save()
				except Exception, e:
					abort(500)
				else:
					session['last_token'] = token
					if token != 'null':
						return redirect("/token/" + token)
					else:
						abort(500)

		# If URI not specified, deal with the VCF upload
		elif request.files['vcf']:

			# Try to get submission upload extension
			try:
				extension = re.compile(r'^.*?[.](?P<extension>' + '|'.join(app.config['UPLOAD_FORMAT_EXTENSIONS']) + ')$').match(request.files['vcf'].filename).group('extension')
			except Exception, e:
				abort(500) # jQuery and WTFoms validation should (hopefully) avoid this...
			else:
				savename = "input." + extension

			# Try to save a record of the submission
			vcf_job = job(  token=token, 
							ip_address=request.remote_addr, 
							submitted=submission_time,
							upload_name=savename,
							min_variant_quality=request.form['min_variant_quality'],
							min_quality_depth=request.form['min_quality_depth'],
							homozyg_window_size=request.form['homozyg_window_size'],
							heterozyg_calls=request.form['heterozyg_calls'])
			try:
				vcf_job.save()
			except Exception, e:
				abort(500)

			# Then try to save the submission file itself
			try:
				upload = vcf_uploads.save(  storage=request.files['vcf'], 
											folder=submission_folder,
											name=savename)
			except Exception, e:
				abort(500)
			else:
				session['last_token'] = token
				if token != 'null':
					return redirect("/token/" + token)
				else:
					abort(500)

		# If nothing, barf.
		else:
			abort(500)

	return render_template("pages/index.html", submission_form=submission_form, token_form=token_form)


@app.route('/misc/allowed_upload_extensions')
def allowed_extensions():
	""" Returns allowed upload extensions. Used by Javascript. Overkill. """
	return "|".join(app.config['UPLOAD_FORMAT_EXTENSIONS'])


@app.route('/misc/no_explanation', methods=['GET'])
def no_explanation():
	""" Turn off token explanation on submission page """
	session['explain_submission'] = False
	return str(session['explain_submission'])


@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static/img'),
							   'favicon.ico',
							   mimetype='image/vnd.microsoft.icon')

