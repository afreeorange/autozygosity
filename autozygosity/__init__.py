from datetime import datetime
from sys import exit

from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine
from flaskext.uploads import UploadSet, configure_uploads, patch_request_class
from flask.ext.assets import Environment, Bundle
from mongoengine.connection import ConnectionError

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

from autozygosity import views, models, helpers, modules

# Configure Jinja2 filters
app.jinja_env.globals.update(get_host_url=helpers.jinja_method_get_hostname)
app.jinja_env.globals.update(explain_submission=helpers.jinja_method_explain_submission)
app.jinja_env.globals.update(max_upload_size=helpers.jinja_method_max_upload_size)

# Configure Jinja2 to compress HTML output
from autozygosity.modules import jinja2htmlcompress
app.jinja_env.add_extension("autozygosity.modules.jinja2htmlcompress.HTMLCompress")

# Set up assets (including jQuery.js breaks things somehow...)
assets = Environment(app)
js = Bundle('js/jquery.ui.min.js', 
			'js/jquery.form.min.js', 
			'js/jquery.validate.min.js', 
			'js/jquery.dataTables.min.js', 
			'js/bootstrap.min.js', 
			'js/bootstrap-slider.min.js', 
			'js/bootstrap-fileupload.min.js',
			'js/autozygosity.js',
			filters='jsmin', output='js/packed.js')
assets.register('autozygosity_js', js)

css = Bundle('css/bootstrap.min.css',
			 'css/bootstrap-responsive.min.css',
			 'css/bootstrap-slider.min.css',
			 'css/bootstrap-fileupload.min.css',
			 'css/autozygosity.css',
			filters='cssmin', output='css/packed.css')
assets.register('autozygosity_css', css)

# Set up routing appropriately
if app.config['APPLICATION_ROOT']:
	from werkzeug.wsgi import DispatcherMiddleware
	routed_app = DispatcherMiddleware(app, {app.config['APPLICATION_ROOT']: app})
else:
	routed_app = app
