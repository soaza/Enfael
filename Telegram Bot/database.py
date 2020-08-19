from firebase import firebase

class Database:
    def __init__(self):
        self.fb = firebase.FirebaseApplication('https://nuscupidbot-5684e.firebaseio.com/', None)
        # load user profile from database
    
    # To retrieve User
    def getUser(self, id):
        if self.fb.get('Profiles', id) == None:
            return None
        return self.fb.get('Profiles', id)

    # Add User for first time setup
    def addUser(self, uid, cid, username):
        self.fb.put('/Profiles/', uid, 
        {'id': uid, 
        'chatID': cid, 
        'username': username,
        'Likes': [0],
        'Dislikes': [0],
        'Matched': "None",
        'userExchange': "None"})

    # Update user data
    def updateUser(self, id, key, value):
        self.fb.put('/Profiles/' + str(id) + '/', key, value)

    def deleteTrait(self, id, key):
        self.fb.delete('/Profiles/', str(id) + '/' + str(key))

    # Sort Profile
    def sortProfile(self, id):
        # BIO to be filtered out in a specific order
        BIO = ['Gender', 'Age', 'Height', 'Weight', 'Appearance', 'Year', 'Major', 'Faculty', 'Trait 1', 'Trait 2', 'Ideal Match']
        sortedProfile = []
        # Finding user in database
        user = self.fb.get('/Profiles/', id)
        # Filtering out
        for key in BIO:
            if key in user:
                sortedProfile.append('{}: {}'.format(key, user[key]))
        return "\n".join(sortedProfile).join(['\n', '\n'])

    # Partner Segment
    def sortPartner(self, id):
        PBIO = ['partnerGender', 'partnerMinAge', 'partnerMaxAge']
        sortedPartner = []
        user = self.fb.get('/Profiles/', id)
        for key, value in user.items():
            if key in PBIO:
                if key == 'partnerGender':
                    sortedPartner.append('Gender: {}'.format(value))
                elif key == 'partnerMinAge':
                    sortedPartner.append('Minimum Age: {}'.format(value))
                if key == 'partnerMaxAge':
                    sortedPartner.append('Maximum Age: {}'.format(value))
        return "\n".join(sortedPartner).join(['\n', '\n'])

    def allProfiles(self):
        return self.fb.get('/Profiles/', None)

    def addLike(self, id, pid):
        user = self.fb.get('/Profiles/', id)
        if pid not in user['Likes']:
            self.fb.put('/Profiles/' + str(id) + '/Likes/', str(pid) , int(pid))

    def addDislike(self, id, pid):
        user = self.fb.get('/Profiles/', id)
        if pid not in user['Dislikes']:
            self.fb.put('/Profiles/' + str(id) + '/Dislikes/', str(pid) , int(pid))

    def deleteUser(self, id):
        self.fb.delete('/Profiles/', id)

    def deleteUserLikes(self, oid, id):
        self.fb.delete('/Profiles/' + str(oid) + '/Likes/', str(id))

    def deleteUserDislikes(self, oid, id):
        self.fb.delete('/Profiles/' + str(oid) + '/Dislikes/', str(id))