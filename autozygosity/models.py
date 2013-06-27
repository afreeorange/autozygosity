from datetime import datetime

from autozygosity import app

from mongoengine import Document, StringField, DateTimeField, ListField
from flask.ext.mongoengine.wtf import model_form

class job(Document):
	token = StringField(required=True, default="alksjsalkd")
	started = DateTimeField(required=True, default=datetime.now())	
	finished = DateTimeField(required=True, default=datetime.now())	
	ip_address = StringField(required=False, default="0.0.0.0")

