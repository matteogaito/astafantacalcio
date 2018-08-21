# -*- coding: utf-8 -*-
from app import app
from flask import render_template


@app.route("/")
def index():
    return render_template('home.html')

@app.route("/error")
def error():
    return render_template('error.html')
