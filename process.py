from flask.ext.script import Manager
from flask.ext.mongoengine import MongoEngine
from mongoengine.connection import ConnectionError

from autozygosity import app, models, db
from autozygosity.helpers import *
from autozygosity.models import job

from lockfile import FileLock
from time import sleep
from pprint import pprint
from datetime import datetime
from subprocess import check_call, CalledProcessError
import sys
import os

# Flask-script management instance
manager = Manager(app)

# Allow only a single analysis process
lock = FileLock('./' + app.config['PROJECT_NAME'].lower().replace(' ', '_'))


def test():
	test = []
	with open('/Users/nikhil/Dropbox/autozygosity/uploads/2013-07-16T14:26:35-jasslem/output.bed') as file:
		for line in file:
			test.append(tuple(line.split()))
	print test


def analyze():
	""" Analyze submitted samples """
	submissions = job.get_submitted()
	analysis_script = app.config['PROJECT_PATH'] + "scripts/run_ROH.sh"
	upload_folder = app.config['UPLOADED_VCF_DEST']

	for submission in submissions:
		input_vcf = upload_folder + "/" + str(submission.submitted.strftime('%Y-%m-%dT%H:%M:%S')) + "-" + submission.token + "/input.vcf"
		try:
			submission.started = datetime.now()
			submission.status = 'running'
			submission.save()
			sleep(5)
			analysis = check_call([analysis_script, input_vcf])
		except CalledProcessError, e:
			submission.status = 'failed'
		else:
			submission.status = 'completed'
		finally:
			submission.finished = datetime.now()
			submission.save()


@manager.command
def start():
	""" Submit jobs for analysis """
	if lock.is_locked():
		sys.exit(0)
	else:
		with lock:
			test()


if __name__ == "__main__":
	manager.run()
