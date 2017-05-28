import os, sqlite3
from threading import Thread
from flask import Flask, render_template, redirect, url_for, send_from_directory, request, session
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from utils import secrets, accounts, recognition, events

app = Flask(__name__)

secrets = secrets.getSecrets()
app.secret_key= secrets['session-key']

app.config['UPLOAD_FOLDER'] = "uploads/"
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = secrets['email']
app.config['MAIL_PASSWORD'] = secrets['email-password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ("Signum Event Systems", secrets['email'])
mail = Mail(app)

#database stuff
cursor = sqlite3.connect("data/data00.db")
query = "CREATE TABLE IF NOT EXISTS users WITH VALUES ()"

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
    '''.format("http://PUTMUTHAFUKKINTECHDOMAINHERE/verify/" + verificationLink)
    sendEmailAsync(app, message)


@app.route("/", methods = ["GET", "POST"])
def home():
    if 'user' in session:
        return render_template("events.html", events = accounts.getEvents(user))
#    else:
#        if 'submit' in request:
            #replacerino
        pass
    else:
        return render_template("index.html")


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    f = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if f and allowed_file(f.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(f.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        recognition.feed_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))
    else:
        return "bad file!"
    
# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

    
if __name__ == "__main__":
    app.debug = True
    app.run()
