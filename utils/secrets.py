def getSecrets():
    secretFile = open("secrets.txt", "r")
    secretArray = secretFile.read().split("\n")
    return {
        'session-key': secretArray[0],
        'email': secretArray[1],
        'email-password': secretArray[2],
        'clarifai-app-id': secretArray[3],
    }

