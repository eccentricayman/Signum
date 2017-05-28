from clarifai.rest import ClarifaiApp

secrets = getSecrets()
client_id = secrets['client-id']
client_secret = secrets['client-secret']
    
#GITIGNORE THIS BOI
app = ClarifaiApp(client_id, client_secret)

app.inputs.create_image_from_url(url="https://samples.clarifai.com/dog1.jpeg", concepts=["cute dog"], not_concepts=["cute cat"])


def uploadPhoto():
    pass

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
