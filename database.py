import json
import os
import logging

class Database:
    def __init__(self):
        self.data = []
        self.logger = logging.getLogger(__name__)

        # load user profile from database
        if not os.path.exists("profiles"):
            os.mkdir('profiles')
        files = os.listdir('profiles')
        for i in range(len(files)):
            with open('profiles/'+files[i], 'r', encoding='utf-8') as fh:
                self.data.append(json.load(fh))
    

    # To retrieve User
    def getUser(self, id):
        for i in range(len(self.data)):
            if(self.data[i]['id'] == id):
                return self.data[i]
        return None


    # Add User for first time setup
    def addUser(self, values):
        self.data.append(values)

    # Save User
    def saveUser(self, id):
        for i in range(len(self.data)):
            if self.data[i]['id'] == id:
                with open('profiles/'+str(id)+'.json', 'w', encoding='utf_8') as fh:
                    fh.write(json.dumps(self.data[i], ensure_ascii=False))

    # Update user data
    def updateUser(self, id, key, value):
        for i in range(len(self.data)):
            if(self.data[i]['id'] == id):
                self.data[i][key] = value
        self.saveUser(id)

    # Sort Profile
    def sortProfile(self, id):
        sortedProfile = []
        for i in range(len(self.data)):
            if(self.data[i]['id'] == id):
                toSortProfile = self.data[i]
        for key, value in toSortProfile.items():
            sortedProfile.append('{}: {}'.format(key, value))
        sortedProfile = sortedProfile[5:]
        return "\n".join(sortedProfile).join(['\n', '\n'])



    # Partner Segment
    def sortPartner(self, id):
        for i in range(len(self.data)):
            if(self.data[i]['id'] == id):
                pGender = self.data[i]['partnerGender']
                pMin = str(self.data[i]['partnerMinAge'])
                pMax = str(self.data[i]['partnerMaxAge'])
        sortedPartnerInfo = ['Gender: {}'.format(pGender), 'Minimum age: {}'.format(pMin), 'Maximum age: {}'.format(pMax)]
        return "\n".join(sortedPartnerInfo).join(['\n', '\n'])

    
    def allProfiles(self):
        return self.data


    def addLike(self, id, bot, context):
        likedPartnerId = self.getUser(id)['lastPartner']
        for i in range(len(self.data)):
            if self.data[i]['id'] == id:
                if likedPartnerId not in self.data[i]['Likes']:
                    self.data[i]['Likes'].append(likedPartnerId)
                    # Check reciprocity
                    partner = None
                    for j in range(len(self.data)):
                        if self.data[j]['id'] == likedPartnerId:
                            partner = self.data[j]
                    if id in partner['Likes']:
                        return partner
                    else:
                        return None
    
    def addDislike(self, id, bot, context):
        dislikedPartnerID = self.getUser(id)['lastPartner']
        for i in range(len(self.data)):
            if self.data[i]['id'] == id:
                if dislikedPartnerID not in self.data[i]['Dislikes']:
                    self.data[i]['Dislikes'].append(dislikedPartnerID)

    def matchedHistory(self, id, oid):
        for i in range(len(self.data)):
            if self.data[i]['id'] == id:
                if oid not in self.data[i]['MatchedHistory']:
                    self.data[i]['MatchedHistory'].append(oid)

    def deleteUser(self, id):
        for i in range(len(self.data)):
            if self.data[i]['id'] == id:
                os.remove('profiles/'+str(self.data[i]['id'])+'.json')
                self.data.remove(self.data[i])
