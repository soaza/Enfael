from firebase import firebase

class Validator:
    def __init__(self):
        self.fb = firebase.FirebaseApplication('https://nuscupidbot-5684e.firebaseio.com/', None)

    # Validates the age
    def validAge(self, age):
        try:
            age = int(age)
            if age > 17 and age < 100:
                return True
            return False
        except:
            return False

    # Check if user essential info setup
    def checkUserMatchReady(self, user):
        keyCheck = ['Gender', 'Age']
        for i in keyCheck:
            if i not in user.keys():
                return False
        else:
            return True

    # Check if partner criteria setup
    def checkPartnerMatchReady(self, user):
        keyCheck = ['partnerGender', 'partnerMinAge', 'partnerMaxAge']
        for i in keyCheck:
            if i not in user.keys():
                return False
        else:
            return True

    # Validates the user's criteria of partner
    def checkPartner(self, user, partner):
        # If user is bisexual
        if user['partnerGender'] == 'Both':
            # Check age range
            if (partner['Age'] >= user['partnerMinAge']) and (partner['Age'] <= user['partnerMaxAge']):
                # Check ids
                if (str(partner['id']) not in user['Likes']) and (str(partner['id']) not in user['Dislikes']) \
                    and (partner['id'] != user['id']):
                    return True
        # If user is monosexual
        # Check age range and which user preferred gender
        if (partner['Age'] >= user['partnerMinAge']) and (partner['Age'] <= user['partnerMaxAge']) and (partner['Gender'] == user['partnerGender']):
            # Check ids
            if (str(partner['id']) not in user['Likes']) and (str(partner['id']) not in user['Dislikes']) \
                and (partner['id'] != user['id']):
                return True
        # No match
        return False

    # Check if mutual
    def checkMatch(self, id, pid):
        user = self.fb.get('/Profiles/', str(id))
        partner = self.fb.get('/Profiles/', str(pid))
        if (str(pid) in user['Likes']) and (str(id) in partner['Likes']):
            return True
        return False

    # Check if exchange user exist
    def checkExchange(self, pid):
        partner = self.fb.get('/Profiles/', str(pid))
        if partner['userExchange'] == 'Accept':
            return 1
        else:
            return 2