from telegram import ReplyKeyboardMarkup, Bot, Update
from validator import Validator
import yaml

class UserHandler:
    def __init__(self, lang):
        self.lang = lang
        self.valid = Validator()
        # All the keyboards markups
        self.markup = {
            'userGender' : ReplyKeyboardMarkup([['Male', 'Female']], one_time_keyboard=True),
            'userBIO' : ReplyKeyboardMarkup([['Gender', 'Age'], ['Height', 'Weight', 'Appearance'], \
                ['Year', 'Major', 'Faculty',], ['Trait 1', 'Trait 2', 'Ideal Match'], ['Remove', 'Done']], one_time_keyboard=True),
            'userBIO2' : ReplyKeyboardMarkup([['Gender', 'Age'], ['Height', 'Weight', 'Appearance'], \
                ['Year', 'Major', 'Faculty',], ['Trait 1', 'Trait 2', 'Ideal Match'], ['Done']], one_time_keyboard=True),
            'partnerBIO' : ReplyKeyboardMarkup([['Partner Gender'], ['Minimum Age', 'Maximum Age'], ['Done']], one_time_keyboard=True),
            'partnerGender' : ReplyKeyboardMarkup([['Male', 'Female', 'Both']], one_time_keyboard=True),
            'matchChoice': ReplyKeyboardMarkup([['Like', 'Dislike'], ['Done']], one_time_keyboard=True),
            'confirmation': ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True),
            'exchange': ReplyKeyboardMarkup([['Accept', 'Reject'], ['Cancel']], one_time_keyboard=True)
            }

    # HANDLES START COMMAND
    def start(self, db, bot, context):
        # Get user information
        uid = bot.message.from_user.id
        user = db.getUser(uid)
        username = bot.message.from_user.username
        # Without a valid username, user cannot use the bot
        if username == None:
            bot.message.reply_text(self.lang['register'])
        # Once they have a valid username
        else:
            bot.message.reply_text(self.lang['start'])
            # If user is not registered before, we prompt him to setup
            if user == None:
                bot.message.reply_text(self.lang['firstTime'])

    # HANDLES PROFILE COMMAND
    def userBIO(self, db, bot, context):
        uid = bot.message.from_user.id
        user = db.getUser(uid)
        if user == None:
            bot.message.reply_text(self.lang['noProfile'])
        else:
            userBIO = db.sortProfile(uid)
            bot.message.reply_text('This is your current profile.\n' + userBIO + '\nYou can edit your profile using /setup.')

    # HANDLES PARTNER COMMAND
    def myPartner(self, db, bot, context):
        uid = bot.message.from_user.id
        user = db.getUser(uid)
        # Check user exist
        if user == None:
            bot.message.reply_text(self.lang['noProfile'])
        # Check if user has a partner
        elif user['Matched'] == 'None':
            # Check if user has a partner which has expired
            if user['userExchange'] != 'None':
                pid = user['userExchange']
                matchedProfile = db.sortProfile(pid)
                bot.message.reply_text('This is your current partner profile.\n' + matchedProfile + \
                    '\nIt appears that your time with your partner is up too. Do initiate an exchange of telegram usernames using /exchange!')
            else:
                bot.message.reply_text(self.lang['noPartner'])
        # When user has a partner
        else:
            pid = user['Matched']
            matchedProfile = db.sortProfile(pid)
            bot.message.reply_text('This is your current partner profile.\n' + matchedProfile + '\nType /message to message your partner '\
                'or type /remove to remove your current partner.')

    # HANDLES HELP COMMAND
    def help(self, bot, context):
        bot.message.reply_text(self.lang['help'])