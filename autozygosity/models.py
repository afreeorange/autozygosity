import re
from datetime import datetime

from autozygosity import app
from helpers import *
from settings import *

from mongoengine import Document, StringField, DateTimeField, ListField, queryset_manager
from flask.ext.mongoengine.wtf import model_form

from flask.ext.wtf import Form, FileField, validators
from wtforms import TextField, ValidationError


class job(Document):
	ip_address = StringField(required=False, default="0.0.0.0")
	token 	   = StringField(required=True,  default=upload_token(2,0))
	status     = StringField(required=True,  default=JOB_STATUSES[0], choices=JOB_STATUSES)
	submitted  = DateTimeField(required=True)
	started    = DateTimeField(required=False)
	finished   = DateTimeField(required=False)	

	@queryset_manager
	def objects(doc_cls, queryset):
		return queryset.order_by('+submitted')

	@queryset_manager
	def get_submitted(doc_cls, queryset):
		return queryset.filter(status='failed')


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
	vcf = FileField(u'Image File', [validators.Required(message = u'You must specify a file')])

	def validate_vcf(form, field):
		m = re.match('^.*\.(' + '|'.join(permute_case('vcf')) + ')$', field.data.filename)
		if not m:
			raise ValidationError('You must upload a VCF file')


class token_form(Form):
	token = StringField(u'Upload token', [validators.Required(message = u'You must specify a token')])

	def validate_token(form, field):
		m = re.match('[a-zA-Z]{5,15}', field.data)
		if not m:
			raise ValidationError('You must supply a valid token')
			
