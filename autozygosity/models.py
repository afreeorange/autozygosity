import re
from datetime import datetime

from autozygosity import app
from helpers import *
from settings import *

from mongoengine import Document, StringField, DateTimeField, ListField, IntField, queryset_manager
from flask.ext.mongoengine.wtf import model_form

from flask.ext.wtf import Form, FileField, TextField, validators
from wtforms import TextField, IntegerField, ValidationError


class job(Document):
	ip_address = StringField(required=False, default="0.0.0.0")
	token 	   = StringField(required=True,  default=generate_token(2,0))
	status     = StringField(required=True,  default=JOB_STATUSES[0], choices=JOB_STATUSES)
	submitted  = DateTimeField(required=True)
	started    = DateTimeField(required=False)
	finished   = DateTimeField(required=False)

	upload_name = StringField(required=True, default="input.vcf")

	min_variant_quality = IntField(min_value=0, max_value=99, default=30)
	min_quality_depth = IntField(min_value=0, default=10)
	homozyg_window_size = IntField(min_value=0, default=1000)
	heterozyg_calls = IntField(min_value=0, default=10)

	meta = {
		'indexes': ['token'],
		'ordering': ['+submitted']
	}

	@queryset_manager
	def objects(doc_cls, queryset):
		return queryset.order_by('+submitted')

	@queryset_manager
	def get_submitted(doc_cls, queryset):
		return queryset.filter(status='submitted')

	@property
	def token_folder(self):
		return self.submitted.strftime('%Y-%m-%dT%H:%M:%S') + "-" + self.token

	@property
	def full_upload_path(self):
		return '/'.join([app.config['UPLOADED_VCF_DEST'], self.token_folder])

	@property
	def input_vcf_path(self):
		return '/'.join([self.full_upload_path, self.upload_name])

	@property
	def output_bed_path(self):
		return '/'.join([self.full_upload_path, 'output.bed'])

	@property
	def output_vcf_path(self):
		return '/'.join([self.full_upload_path, 'output.ROH.vcf'])

	@property
	def output_zip_path(self):
		return '/'.join([self.full_upload_path, 'output.zip'])

	@property
	def logfile_path(self):
		return '/'.join([self.full_upload_path, 'analysis.log'])


# Don't really use this anywhere right now. Maybe a future release :)
class joblog:
	def __init__(self, token):
		self.logger = logging.getLogger(token)
		self.logger.setLevel(logging.DEBUG)

		# Set the format (using ISO8601 for date)
		logformat = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
									  datefmt = '%Y-%m-%dT%H:%M:%S')
		# Create a handler
		loghandler = logging.StreamHandler()
		loghandler.setLevel(logging.DEBUG)
		loghandler.setFormatter(logformat)

		# Attach handler to logger
		self.logger.addHandler(loghandler)

	@property
	def logger(self):
		return self.logger



class job_form(Form):
	vcf = FileField(u'VCF File', [validators.Required(message = u'You must specify a file')])

	min_variant_quality = IntegerField(u'Minimum Variant Quality', [validators.NumberRange(min=0, max=99)], default=30)
	min_quality_depth = IntegerField(u'Minimum Quality by Depth', [validators.NumberRange(min=0)], default=10)
	homozyg_window_size = IntegerField(u'Homozygosity Window Size', [validators.NumberRange(min=0)], default=1000)
	heterozyg_calls = IntegerField(u'Heterozygous Calls allowed in window', [validators.NumberRange(min=0)], default=10)

	def validate_vcf(form, field):
		m = re.match('^.*\.(' + '|'.join(app.config['UPLOAD_FORMAT_EXTENSIONS']) + ')$', field.data.filename, re.IGNORECASE)
		if not m:
			raise ValidationError(u'You must upload a VCF file (compressed options are .zip, .gz, .tgz, and .tar.gz)')


class check_form(Form):
	token = TextField(u'Submission token', [validators.required(message = u'You must specify a submission token')])

	def validate_token(form, field):
		m = re.match(app.config['TOKEN_REGEX'], field.data)
		if not m:
			raise ValidationError(u'You must supply a valid token')
			
class uri_submit_form(Form):
	uri = TextField(u'VCF URI', [validators.required(message = u'You must specify a URI'), validators.URL(message = u'You must specify a valid URI (e.g. "localhost" is not allowed)')])
