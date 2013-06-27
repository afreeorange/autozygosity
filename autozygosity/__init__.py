from sys import exit
from datetime import datetime

from flask import Flask
from jinja2 import Environment
from flask.ext.mongoengine import MongoEngine
from mongoengine.connection import ConnectionError

app = Flask(__name__)
app.config.from_object('settings')
app.config['CSRF_ENABLED'] = True
app.config['CURRENT_YEAR'] = datetime.now().strftime("%Y")

try:
    db = MongoEngine(app)
except ConnectionError, e:
    print str(e)
    print "----"
    print "Are you sure your MongoDB instance is running?"
    print "If on another server or port, look at settings.py."
    exit(1) 

from autozygosity import views, models

if __name__ == '__main__':
    app.run()

