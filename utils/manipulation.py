from pymongo import MongoClient
import gridfs
import hashlib
import string
import random

#database
connection = MongoClient("127.0.0.1")
db = connection['Signum']
filesystem = gridfs.GridFS(db)
users = db['users']
events = db['events']

#miscellaneous
def getVerificationLink():
    link = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
    #check if any other users have this id
    check = db.users.count(
        {
            'verificationLink': link
        }
    )
    #if the id isn't unique, recursively run and get another id
    if check:
        link = getVerificationLink()
        return link
    else:
        return link

def getEventID():
    identification = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
    check = db.events.count(
        {
            'id': identification
        }
    )
    if check:
        identification = getEventID()
        return identification
    else:
        return identification

#users
def addUser(email, password):
    check = users.count({ 'email': email })
    if not(check):
        link = getVerificationLink()
        users.insert(
            {
                'name': '',
                'email': email,
                'password': hashlib.sha256(password).hexdigest(),
                'question': '',
                'answer': '',
                'images': [],
                'events': [],
                'eventsCreated': [],
                'verified': False,
                'verificationLink': link,
                'setup': False
            }
        )
        return link
    else:
        return False

def updateUserName(email, name):
    user = getUser(email)
    if user:
        user['name'] = value
        return True
    else:
        return False
        
def updateUserMainImage(email, image):
    user = getUser(email)
    if user:
        removeImage(user['images'][0])
        addUserImage(email, image, True)
        return True
    else:
        return False

def updateQuestion(email, question, answer):
    user = getUser(email)
    user['question'] = question
    user['answer'] = answer
    
def setupUser(email, name, mainImage, question, answer):
    user = getUser(email)
    if user['setup']:
        return False
    else:
        updateUserName(email, name)
        updateUserMainImage(email, mainImage)
        updateQuestion(email, question, answer)
        user['setup'] = True
        return True

def updateUserEmail(oldemail, newemail):
    check = users.count({ 'email': newemail })
    if check != 0:
        return (False, "An account already exists with that email.")
    else:
        user = getUser(oldemail)
        user['email'] = newemail
        user['verified'] = False

        link = getVerificationLink()
        user['verificationLink'] = link
        sendVerificationEmail(newemail, link)
        return (True, "")

def authenticateUser(email, password):
    check = users.count({ 'email': email })
    #if check is empty, no users with that email
    if not(check):
        return (False, "User doesn't exist.")
    else:
        if hashlib.sha256(password).hexdigest() == getUser(email)['password']:
            return (True, "")
        else:
            return (False, "Incorrect password.")
    
def getUser(email):
    return users.find_one({ 'email': email })

#get the events the user created
def getUserEvents(email):
    events = getUser(email)['eventsCreated']
    retEvents = []
    for event in events:
        retEvents.append(getEvent(event))
        retEvents[-1]['image'] = getEventImage(retEvents[-1]['image'])
    return retEvents

#gets the users events attending
def getUsersEvents(email):
    events = getUser(email)['events']
    retEvents = []
    for event in events:
        retEvents.append(getEvent(event))
    return retEvents

def getUserImages(email):
    images = getUser(email)['images']
    retImages = []
    for image in images:
        retImages.append(getImage(image))
    return retImages
    
def addUserImage(email, image, main):
    user = getUser(email)
    #can't find user
    if not(user):
        return False

    fileID = addImage(image)
    #updating main image
    if main:
        user['images'][0] = fileID
    else:
        users['images'].append(fileID)
    return True

#events
#date is string
#MM/DD/YYYY
def addEvent(name, creator, location, date, image):
    fileID = addImage(image)
    eventID = getEventID()
    
    user = getUser(creator)
    user['eventsCreated'].append(eventID)
    
    events.insert(
        {
            'name': name,
            'creator': creator,
            'id': eventID,
            'location': location,
            'date': date,
            'image': fileID,
            'users': []
        }
    )
    return eventID
    
def getEvent(eventID):
    return events.find_one({ 'id': eventID })

def getEventImage(eventID):
    return getImage(getEvent(eventID)['image'])

def updateEventName(eventID, name):
    event = getEvent(eventID)
    event['name'] = name

def updateEventLocation(eventID, location):
    event = getEvent(eventID)
    event['location'] = location

def updateEventDate(eventID, date):
    event = getEvent(eventID)
    event['date'] = date

def updateEventImage(eventID, image):
    event = getEvent(eventID)
    removeImage(event['image'])
    event['image'] = addImage(image)

def removeEvent(eventID):
    event = getEvent(eventID)
    user = getUser(event['creator'])
    user['eventsCreated'].remove(eventID)
    
    db.events.remove(
        {
            'id': eventID
        }
    )
    
def addUserToEvent(eventID, email):
    event = getEvent(eventID)
    event['users'].append(email)

def removeUserFromEvent(eventID, email):
    event = getEvent(eventID)
    event['users'].remove(email)

#images
def addImage(image):
    return fs.put(image)

def getImage(imageID):
    return fs.get(imageID)

def removeImage(imageID):
    return fs.delete(imageID)
