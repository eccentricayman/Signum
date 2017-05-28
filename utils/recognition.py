from clarifai.rest import ClarifaiApp

client_id = ""
client_secret = ""
with open("utils/client_secret.txt") as secrets_file:
    data = secrets_file.read().split("\n")
    client_id = data[0]
    client_secret = data[1]
    
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
