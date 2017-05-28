import os, gridfs
from pymongo import MongoClient
from threading import Thread
from flask import Flask, render_template, redirect, url_for, send_from_directory, request, session, flash
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from utils import secrets, manipulation, recognition
from pprint import pprint

app = Flask(__name__)

secrets = secrets.getSecrets()
app.secret_key= secrets['session-key']
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = secrets['email']
app.config['MAIL_PASSWORD'] = secrets['email-password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config['MAIL_DEFAULT_SENDER'] = ("Signum Event Systems", secrets['email'])

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

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
    '''.format("http://signumsystems.tech/verify/" + verificationLink)
    sendEmailAsync(app, message)


@app.route("/", methods = ["GET", "POST"])
def home():
    #session.clear()
    if 'user' in session:
        return render_template("events.html", createdEvents = manipulation.getUserEvents(session['user']), joinedEvents = manipulation.getUsersEvents(session['user']))
    else:
        if request.method == "POST":
            if "login" in request.form:
                email = request.form['email']
                password = request.form['password']
                check = manipulation.authenticateUser(email, password)
                
                if check[0]:
                    session['user'] = email
                    #already setup
                    if manipulation.getUser(email)['setup']:
                        #go to events
                        return render_template("events.html", eventsAttending = manipulation.getUsersEvents(email), eventsCreated = manipulation.getUserEvents(email))
                    #go to setup
                    else:
                        return render_template("setup.html", user = manipulation.getUser(email))
                #go to main with error message
                else:
                    return render_template("index.html", message = check[1])
            #my dude trynna signup?
            elif 'register' in request.form:
                email = request.form['email']
                password = request.form['password']
                check = db.users.count({ 'email': email })
                if check:
                    return render_template("index.html", message = "An account already exists with that email.")
                else:
                    link = manipulation.addUser(email, password)
                    sendVerificationEmail(email, link)
                    return render_template("index.html", message = "A verification email has been sent to {0}".format(email))
            #this is for setup
            elif "setup" in request.form:
                email = session['user']
                name = request.form['name']
                question = request.form['question']
                answer = request.form['answer']
                
                image = request.files['image']
                if image.filename == "":
                    return render_template("setup.html", message = "You should upload an image!")
                if image and allowed_file(image.filename):
                    manipulation.setupUser(email, name, image, question, answer)
            #here is events page
            else:
                pass
        #go to login/signup
        else:
            return render_template("index.html")
        

@app.route('/test')
def test():
    return render_template("upload.html")

        
# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    f = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if f and allowed_file(f.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(f.filename)
        # Movethe file form the temporal folder to
        # the upload folder we setup
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(path)
        if recognition.isProperPhoto(path):
            name = request.form.get("name")
            recognition.feed_image(path, name)

            # Redirect the user to the uploaded_file route, which
            # will basicaly show on the browser the uploaded file
            return redirect(url_for('uploaded_file',
                            filename=filename))
        else:
            return "not a proper photo!!"
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

@app.route('/predict')
def predict():
    return render_template("predict.html")

# Route that will process the file upload
@app.route('/upload_predict', methods=['POST'])
def upload_predict():
    # Get the name of the uploaded file
    f = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if f and allowed_file(f.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(f.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(path)
        if recognition.isProperPhoto(path):
            # Move the file form the temporal folder to
            # the upload folder we setup
            prediction = recognition.getPrediction(path)
            os.remove(path)
            data = prediction["outputs"][0]["data"]["concepts"]
            s = ""
            for point in data:
                s += point["name"] + ": " + str(point["value"] * 100) + "% confidence\n"
            return render_template("kek.html", message=s)
        else:
            return "not a valid face pic!!!"
    else:
        return "bad file!"

    
@app.route('/event/<eventid>', methods=['GET', 'POST'])
# joining a event
def singleEvent(eventid):
    if 'join' in request.form:
        manipulation.addUserToEvent(request.form['join'], session['user'])
        #creating an event
    else:
        name = request.form['name']
        creator = session['user']
        location = request.form['location']
        date = request.form['date']
        
        image = request.files['image']
        if image.filename == "":
            return render_template("events.html", message = "You should add an image to showcase your event!")
        
        if image and allowed_file(image.filename):
            manipulation.addEvent(name, creator, location, date, image)
            
            return redirect(url_for("home"))
            #go to lgin/signup / landing page
        else:
            return render_template("index.html")



@app.route("/serve")
def serve():
    render_template("serve.html")

    
@app.route("/verify/<link>", methods=["GET", "POST"])
def verify(link):
    users = db.users.find({})
    for user in users:
        if user['verificationLink'] == link:
            user['verified'] = True
            return redirect(url_for("home", message = "Your account has been verified."))
    return redirect(url_for("home", message = "Invalid verification link."))



@app.route('/event/<eventid>')
def eventPage(eventid):
    event = manipulation.getEvent(eventid)
    eventImage = manipulation.getEventImage(eventid)
    if event:
        if session['user'] == event['creator']:
            return redirect(url_for("/control/{0}".format(event['id'])))
        else:
            return render_template("event.html", event = event, image = eventImage)
    else:
        return redirect(url_for("home"))

    
@app.route('/leave/<eventid>')
def leaveEvent(eventid):
    event = manipulation.getEvent(eventid)
    if event and session['user']:
        event['users'].remove(session['user'])
    else:
        return redirect(url_for("home"))

    
@app.route("/control/<eventid>")
def controlEvent(eventid):
    event = manipulation.getEvent(eventid)

if __name__ == "__main__":
    app.debug = True
    app.run()
