class Validator:
    def __init__(self):
        self = None

    # Validates the age
    def validAge(self, age):
        try:
            age = int(age)
            if age > 17 and age < 100:
                return True
            return False
        except:
            return False
    
    # Validates the height
    def validHeight(self, height):
        try:
            height = int(height)
            if height > 63 and height < 272:
                return True
            return False
        except:
            return False

    # Validates the weight
    def validWeight(self, weight):
        try:
            weight = int(weight)
            if weight > 30 and weight < 220:
                return True
            return False
        except:
            return False

    # Validates the user's criteria of partner
    def checkPartner(self, user, partner):
        # If user is bisexual
        if user['partnerGender'] == 'Both':
            # Check age range
            if (partner['Age'] >= user['partnerMinAge']) and (partner['Age'] <= user['partnerMaxAge']):
                # Check id
                if (partner['id'] not in user['Likes']) and (partner['id'] not in user['Dislikes']) and (partner['MatchedHistory'] not in user['MatchedHistory']):
                    return True

        # If user is monosexual
        # Check age range and which user preferred gender
        elif (partner['Age'] >= user['partnerMinAge']) and (partner['Age'] <= user['partnerMaxAge']) and (partner['Gender'] == user['partnerGender']):
            # Check id
            if (partner['id'] not in user['Likes']) and (partner['id'] not in user['Dislikes']) and (partner['MatchedHistory'] not in user['MatchedHistory']):
                return True

        # No match
        return False