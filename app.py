import os
from threading import Thread
from flask import Flask, render_template, redirect, url_for, send_from_directory, request, session
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from utils import secrets

secrets = secrets.getSecrets()
app['SECRET_KEY'] = secrets['session-key']

app.config['UPLOAD_FOLDER'] = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = secrets['email']
app.config['MAIL_PASSWORD'] = secrets['email-password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ("Signum", secrets['email'])

@app.route("/")
def home():
    if ['user'] in session:
        return getEvents(session['user'])
    else:
        return render_template("index.html")

def getEvents(user):
    
