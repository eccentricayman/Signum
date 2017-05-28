import os, gridfs
from pymongo import MongoClient
from threading import Thread
from flask import Flask, render_template, redirect, url_for, send_from_directory, request, session
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from utils import secrets, manipulation, recognition

app = Flask(__name__)

secrets = secrets.getSecrets()
app.secret_key= secrets['session-key']

app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = secrets['email']
app.config['MAIL_PASSWORD'] = secrets['email-password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ("Signum Event Systems", secrets['email'])
mail = Mail(app)

#database stuff
connection = MongoClient("127.0.0.1")
db = connection['Signum']
filesystem = gridfs.GridFS(db)
users = db['users']
events = db['events']

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#mail functions
#here is async wrapper for mail
def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

#forces flask-mail to send email asynchronously
@async
def sendEmailAsync(app, message):
    with app.app_context():
        mail.send(message)

#this sends a mail, with email and verification link
def sendVerificationEmail(email, verificationLink):
    message = Message()
    message.recipients = [ email ]
    message.subject = "Confirm Your Signum Account"
    message.html = '''
    <center>
<h1 style="font-weight: 500 ; font-family: Arial">Signum</h1>
    <p style="font-weight: 500 ; font-family: Arial">Thanks for signing up for Signum! Please press the button below to verify your account.</p>
    <br><br>
    <a href="{0}" style="padding: 1.5% ; text-decoration: none ; color: #404040; border: 1px solid black ; text-transform: uppercase ; font-weight: 500 ; font-family: Arial ; padding-left: 10% ; padding-right: 10%">Verify Email</a>
</center>
    '''.format("http://127.0.0.1/verify/" + verificationLink)
    sendEmailAsync(app, message)


@app.route("/", methods = ["GET", "POST"])
def home():
    if 'user' in session:
        return render_template("events.html", events = manipulation.getUserEvents(session['user']))
    else:
        if request.form:
            if request.form['submit'] == "login":
                email = request.form['email']
                password = request.form['password']
                check = manipulation.authenticateUser(email, password)
                
                if check[0]:
                    session['user'] = email
                    #already setup
                    if getUser(email)['setup']:
                        #go to events
                        return render_template("events.html", eventsAttending = getUsersEvents(email), eventsCreated = getUserEvents(email))
                    #go to setup
                    else:
                        return render_template("setup.html", user = getUser(email))
                #go to main with error message
                else:
                    return render_template("index.html", message = check[1])
            #my dude trynna signup?
            else:
                
        #go to lgin/signup
        else:
            return render_template("index.html")

        
#@app.route('/event/<eventid>', methods=['POST'])
def eventPage(eventid):
    event = getEvent()
    
if __name__ == "__main__":
    app.debug = True
    app.run()
