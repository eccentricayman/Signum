from clarifai.rest import ClarifaiApp
import secrets

secrets = secrets.getSecrets()
client_id = secrets['client-id']
client_secret = secrets['client-secret']
    
#GITIGNORE THIS BOI
clar_app = ClarifaiApp(client_id, client_secret)



model = None

try:
    model = clar_app.models.create(model_id="pets", concepts=["cute cat", "cute dog"])
    
def feed_image(filename):
    clar_app.inputs.create_image_from_url(url=filename, concepts=[""], not_concepts=["cute cat"])

'''
gets two images
one is original, one is new
check if face in new image is same person as face in original
'''
def facialComparison(originals, toCompare):
    pass



'''
check if image is proper face
'''
def properPhoto(photo):
    pass
