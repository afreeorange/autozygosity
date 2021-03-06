from flask.ext.mongoengine import MongoEngine
from flask.ext.script import Manager
from mongoengine.connection import ConnectionError

from autozygosity import app, models, db
from autozygosity.helpers import *
from autozygosity.models import job

from datetime import datetime, timedelta
from lockfile import FileLock
from shutil import rmtree
from subprocess import check_call, CalledProcessError
from sys import exit
from time import sleep
import shlex

# Flask-script management instance
manager = Manager(app)

# Allow only a single analysis process
lock = FileLock('./' + app.config['PROJECT_NAME'].lower().replace(' ', '_'))


@manager.command
def clean():
	""" Clean uploads folder and MongoDB of all files and tokens older than X days """
	old_submissions = job.objects(submitted__lt=datetime.now() - timedelta(days=app.config['SUBMISSION_RETENTION_DAYS']))
	
	for submission in old_submissions:
		print "> Processing", submission.token
		try:
			rmtree(submission.full_upload_path)
		except Exception, e:
			print "!", str(e)
		submission.delete()


@manager.command
def analyze():
	""" Analyze submitted samples """
	submissions = job.get_submitted()
	analysis_script = app.config['PROJECT_PATH'] + "scripts/run.sh"
	upload_folder = app.config['UPLOADED_VCF_DEST']

	for submission in submissions:
		try:
			submission.started = datetime.now()
			submission.status = 'running'
			submission.save()
			print submission.started, "Starting", submission.token, "from", submission.ip_address
			check_call(analysis_script + ' '
						+ ' -i ' + submission.input_vcf_path
						+ ' -v ' + str(submission.min_variant_quality)
						+ ' -d ' + str(submission.min_quality_depth)
						+ ' -w ' + str(submission.homozyg_window_size)
						+ ' -c ' + str(submission.heterozyg_calls)
						+ ' -z '
						+ ' &> ' + submission.full_upload_path + '/analysis.log'
						, shell=True)
		except CalledProcessError, e:
			submission.status = 'failed'
		else:
			submission.status = 'completed'
		finally:
			submission.finished = datetime.now()
			print submission.finished, "Finished", submission.token
			submission.save()


if __name__ == "__main__":
	if lock.is_locked():
		exit(0)
	else:
		with lock:
			manager.run()
