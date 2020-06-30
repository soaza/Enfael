from telegram import ReplyKeyboardMarkup, Bot, Update
from validator import Validator
from telegram.ext import CommandHandler
import logging

class UserHandler:
    def __init__(self):
        self.valid = Validator()
        self.logger = logging.getLogger(__name__)
        # All the keyboards markups
        self.markup = {
            'userGender' : ReplyKeyboardMarkup([['Male', 'Female']], one_time_keyboard=True),

            'userBIO' : ReplyKeyboardMarkup([['Height', 'Weight', 'Appearance'], \
                ['Year', 'Major', 'Faculty',], ['Trait 1', 'Trait 2', 'Ideal Match'], ['DONE']], one_time_keyboard=True),

            'partnerGender' : ReplyKeyboardMarkup([['Male', 'Female', 'Both']], one_time_keyboard=True),

            # To decide on user choices on other profiles
            'searchChoice': ReplyKeyboardMarkup([['Like', 'Dislike'], ['DONE']], one_time_keyboard=True),

            # Typical Yes No keyboard
            'yesNo': ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)
            }


    def myProfile(self, db, bot, context):
        uid = str(bot.message.from_user.id)
        myprofile = db.sortProfile(int(uid))
        bot.message.reply_text('This is your profile so far.\n' + myprofile + '\nWould you like to change anything?')


    def myMatch(self, db, bot, context):
        uid = str(bot.message.from_user.id)
        mid = db.getUser(int(uid))['Matched']
        matchedProfile = db.sortProfile(mid)
        bot.message.reply_text('This is your matched profile.\n' + matchedProfile + '\nType /message to message your match '\
            'or type /remove to remove your current match.')




