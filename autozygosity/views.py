import os

from flask import Flask, render_template, send_from_directory, request, redirect, url_for, abort
from autozygosity import app
from models import job

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

