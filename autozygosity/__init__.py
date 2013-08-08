from sys import exit
from datetime import datetime

from flask import Flask, render_template
from jinja2 import Environment
from flask.ext.mongoengine import MongoEngine
from mongoengine.connection import ConnectionError

from flaskext.uploads import UploadSet, configure_uploads, patch_request_class

# Configure Flask app
app = Flask(__name__)
app.config.from_object('settings')

# Configure uploads
vcf_uploads = UploadSet(name = 'vcf', extensions = tuple(app.config['UPLOAD_FORMAT_EXTENSIONS']))
configure_uploads(app, vcf_uploads)
patch_request_class(app, app.config['UPLOADED_VCF_MAX_SIZE']) # 128MB max upload size

# Attempt connection to MongoDB instance
try:
	db = MongoEngine(app)
except ConnectionError, e:
	print str(e)
	print "----"
	print "Are you sure your MongoDB instance is running?"
	print "If on another server or port, look at settings.py."
	exit(1) 

from autozygosity import views, models, helpers
app.jinja_env.globals.update(get_host_url=helpers.jinja_method_get_hostname)
app.jinja_env.globals.update(explain_submission=helpers.jinja_method_explain_submission)
app.jinja_env.globals.update(max_upload_size=helpers.jinja_method_max_upload_size)

# Set up routing
if app.config['APPLICATION_ROOT']:
	from werkzeug.wsgi import DispatcherMiddleware
	routed_app = DispatcherMiddleware(app, {app.config['APPLICATION_ROOT']: app})
else:
	routed_app = app
