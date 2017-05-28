from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as CImage
import secrets
from pprint import pprint
from pymongo import MongoClient
import gridfs

#database                                                 
connection = MongoClient("127.0.0.1")
db = connection['Signum']
filesystem = gridfs.GridFS(db)
users = db['users']
events = db['events']

secrets = secrets.getSecrets()
client_id = secrets['client-id']
client_secret = secrets['client-secret']
    
clar_app = ClarifaiApp(client_id, client_secret)

model = None
#clar_app.models.delete(model_id="faces")

try:
    model = clar_app.models.create(model_id="faces", concepts_mutually_exclusive=False, concepts=[])
except:
    model = clar_app.models.get(model_id="faces")
    
def feed_image(filename, name):
    global model
    names = model.get_concept_ids()

#    print "name: " + str(name)
#    print "names: " + str(names)
    if name in names:
        clar_app.inputs.create_image_from_filename(filename, concepts=[name], not_concepts=names.remove(name))
    else:
        model.add_concepts([name])
        clar_app.inputs.create_image_from_filename(filename, concepts=[name], not_concepts=names)
        model = model.train()    


def getPrediction(filename):
    global model
    prediction = model.predict_by_filename(filename=filename)
    pprint(prediction)
    return prediction



'''
check if image is proper face
'''
def isProperPhoto(filename):
    faceDetModel = clar_app.models.get('face-v1.3')
    image = CImage(filename=filename)
    resp = faceDetModel.predict([image])
    return "regions" in resp["outputs"][0]["data"] and len(resp["outputs"][0]["data"]["regions"]) == 1
