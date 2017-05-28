def getSecrets():
    secretFile = open("secrets.txt", "r")
    secretArray = secretFile.read().split("\n")
    return {
        'session-key': secretArray[0],
        'email': secretArray[1],
        'email-password': secretArray[2],
        'client-id': secretArray[3],
        'client-secret': secretArray[4]
    }

