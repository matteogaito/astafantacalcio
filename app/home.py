# -*- coding: utf-8 -*-
from app import app
from flask import render_template, request

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import TextField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

from wtforms.validators import Required

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/aste")
def aste():
    return render_template('aste.html')

@app.route("/error")
def error():
    return render_template('error.html')

class ContactForm(FlaskForm):
    name = TextField("Name")
    email = TextField("Email")
    subject = TextField("Subject")
    message = TextAreaField("Message")
    recaptcha = RecaptchaField()
    submit = SubmitField("Send")

@app.route('/contatti', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    print(app.testing)

    if request.method == 'POST':
        return 'Form posted.'

    elif request.method == 'GET':
        return render_template('contact.html', form=form)
