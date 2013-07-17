from flask.ext.mongoengine import MongoEngine
from flask.ext.script import Manager
from mongoengine.connection import ConnectionError

from autozygosity import app, models, db
from autozygosity.helpers import *
from autozygosity.models import job

from datetime import datetime, timedelta
from lockfile import FileLock
from pprint import pprint
from subprocess import check_call, CalledProcessError
from time import sleep
import os
import sys
from shutil import rmtree

# Flask-script management instance
manager = Manager(app)

# Allow only a single analysis process
lock = FileLock('./' + app.config['PROJECT_NAME'].lower().replace(' ', '_'))


@manager.command
def clean():
	""" Clean uploads folder and MongoDB of all files and tokens older than X days """
	submissions = job.objects(submitted__lt=datetime.now() - timedelta(days=app.config['SUBMISSION_RETENTION_DAYS']))
	
	for submission in submissions:
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
			check_call([analysis_script, submission.input_vcf_path])
		except CalledProcessError, e:
			submission.status = 'failed'
		else:
			submission.status = 'completed'
		finally:
			submission.finished = datetime.now()
			submission.save()


if __name__ == "__main__":
	""" Decorator to ensure that only a single manager process runs at a time """
	if lock.is_locked():
		sys.exit(0)
	else:
		with lock:
			manager.run()
