import logging
from database import Database
from userhandler import UserHandler
from validator import Validator
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# For conversation handlers
UGENDER, UAGE, UBIO, UREPLIES, PGENDER, PMINAGE, PMAXAGE, MCHOICE, REPLIES = range(9)





# START COMMAND
def start(bot, context):
    # Get user information
    uid = str(bot.message.from_user.id)
    user = db.getUser(int(uid))
    username = bot.message.from_user.username

    # Without a valid username, user cannot use the bot
    if username == None:
        bot.message.reply_text('Please kindly register a username on Telegram before using me! Click /start to try again.')

    # Once they have a valid username
    else:
        bot.message.reply_text('Hello! I am the NUS Blind Cupid Bot! ' \
        'I can help you set up a love profile for you to advertise yourself and hopefully find a match!' \
            '\n\nYou can control me by sending me these commands.' \
                '\n\n/setup - to setup/edit your profile\n/profile - to see your profile' \
                    '\n/partner - to see your partner criteria\n/match - to start looking for profiles'\
                        '\n/message - to message your partner\n/matched - to view your current match profile'\
                            '/remove - to remove your partner\n/delete - to delete your profile')
                    
        
        # If user is not registered before, we prompt him to setup
        if user == None:
            bot.message.reply_text('This is your first time using this bot! Setup your profile using /setup.')
        else:
            bot.message.reply_text('Welcome back!')





# SETUP COMMAND
def setup(bot, context):
    uid = str(bot.message.from_user.id)
    user = db.getUser(int(uid))
    cid = bot.message.chat_id
    if user == None:
        db.addUser({'id': int(uid), 'chatID': int(cid), 'Likes': [], 'Dislikes': [], 'MatchedHistory': [], 'Matched': None})
        db.saveUser(int(uid))
        bot.message.reply_text('What is your gender?', reply_markup=uHandler.markup['userGender'])
        return UGENDER
    else:
        bot.message.reply_text('This is your account. Would you like to edit anything?')


# User Gender
def userGender(bot, context):
    uid = str(bot.message.from_user.id)
    if bot.message.text == 'Male':
        db.updateUser(int(uid), 'Gender', 'Male')
    elif bot.message.text == 'Female':
        db.updateUser(int(uid), 'Gender', 'Female')
    else:
        bot.message.reply_text('Invalid input: Please indicate either Male or Female.')
        return
    bot.message.reply_text('Now tell me your age.')
    return UAGE

# User Age
def userAge(bot, context):
    uid = str(bot.message.from_user.id)
    if valid.validAge(bot.message.text):
        db.updateUser(int(uid), 'Age', int(bot.message.text))
        bot.message.reply_text('Nice! Which other traits would you like to tell me?', reply_markup=uHandler.markup['userBIO'])
        return UBIO
    else:
        bot.message.reply_text('Invalid input: Please return an integer from 18 to 100')
        return

def userBio(bot, context):
    uid = str(bot.message.from_user.id)
    topic = bot.message.text
    context.user_data['topic'] = topic
    if context.user_data.get(topic):
        bot.message.reply_text('Your {}, I already know the following about that: {}'.format(topic.lower(), context.user_data[topic]))
    else:
        bot.message.reply_text('Your {}? Yes I would love to hear about that!'.format(topic.lower()))
    return UREPLIES

# The information the user gave so far
def userReplies(bot, context):
    uid = str(bot.message.from_user.id)
    topic = context.user_data['topic']
    answer = bot.message.text
    db.updateUser(int(uid), topic, answer)
    bot.message.reply_text('Nicely done! Would you like to tell me more?', reply_markup=uHandler.markup['userBIO'])                              
    return UBIO

# To exit the conversation setup
def uDone(bot, context):
    uid = str(bot.message.from_user.id)
    del context.user_data['topic']
    myprofile = db.sortProfile(int(uid))
    bot.message.reply_text('This is your profile so far.\n' + myprofile + '\nWould you like to change anything?')
    return ConversationHandler.END


# MYPROFILE COMMAND
def userProfile(bot, context):
    return uHandler.myProfile(db, bot, context)




# PARTNERPROFILE
def myPartner(bot, context):
    uid = str(bot.message.from_user.id)
    user = db.getUser(int(uid))
    if 'partnerGender' not in user:
        bot.message.reply_text('Looks like you never talk about your ideal partner before. '\
            'What is your ideal partner age?', reply_markup=uHandler.markup['partnerGender'])
        return PGENDER
    else:
        partnerInfo = db.sortPartner(int(uid))
        bot.message.reply_text('This is your ideal partner information.\n' + partnerInfo + '\nWould you like to change anything?')


def partnerGender(bot, context):
    uid = str(bot.message.from_user.id)
    if bot.message.text == 'Male':
        db.updateUser(int(uid), 'partnerGender', 'Male')
    elif bot.message.text == 'Female':
        db.updateUser(int(uid), 'partnerGender', 'Female')
    elif bot.message.text == 'Both':
        db.updateUser(int(uid), 'partnerGender', 'Both')
    else:
        bot.message.reply_text('Invalid input: Please indicate either Male, Female, or both.')
        return
    bot.message.reply_text('Now, tell me your ideal match minimum age.')
    return PMINAGE

def partnerMinAge(bot, context):
    uid = str(bot.message.from_user.id)
    if valid.validAge(bot.message.text):
        db.updateUser(int(uid), 'partnerMinAge', int(bot.message.text))
        bot.message.reply_text('Ok, now tell me your ideal match maximum age.')
        return PMAXAGE
    else:
        bot.message.reply_text('Invalid input: Please return an integer from 18 to 100')
        return

def partnerMaxAge(bot, context):
    uid = str(bot.message.from_user.id)
    if valid.validAge(bot.message.text):
        db.updateUser(int(uid), 'partnerMaxAge', int(bot.message.text))
        partnerInfo = db.sortPartner(int(uid))
        bot.message.reply_text('This is your ideal partner information.\n' + partnerInfo + '\nYou can start looking for matches using /match')
        return ConversationHandler.END
    else:
        bot.message.reply_text('Invalid input: Please return an integer from 18 to 100')

def pDone(bot, context):
    uid = str(bot.message.from_user.id)
    del context.user_data['topic']
    myprofile = db.sortProfile(int(uid))
    bot.message.reply_text('This is your profile so far.\n' + myprofile + '\nWould you like to change anything?')
    return ConversationHandler.END







# MATCHING 
def match(bot, context):
    uid = str(bot.message.from_user.id)
    user = db.getUser(int(uid))
    if user['Matched'] != None:
        bot.message.reply_text('You already have a match. Type /message to text your match or /remove to remove your current match.')
        return ConversationHandler.END
    else:
        # Start finding potential matches
        for i in range(len(db.allProfiles())):
            if valid.checkPartner(user, db.allProfiles()[i]):
                partner = db.allProfiles()[i]
                db.updateUser(int(uid), 'lastPartner', partner['id'])
                partnerProfile = db.sortProfile(partner['id'])
                bot.message.reply_text(partnerProfile, reply_markup=uHandler.markup['searchChoice'])
                return MCHOICE
        # If no more partners
        bot.message.reply_text('You ran out of potential partners! Try again in a few days when more people join. Help spread the bot!')


def mChoice(bot, context):
    uid = str(bot.message.from_user.id)
    pid = db.getUser(int(uid))['lastPartner']
    if bot.message.text == 'Like':
        mutually = db.addLike(int(uid), bot, context)
        if mutually != None:
            bot.message.reply_text('Congratulation you matched! Message your match using /message.')
            db.matchedHistory(int(uid), pid)
            db.matchedHistory(pid, int(uid))
            db.updateUser(int(uid), 'Matched', pid)
            db.updateUser(pid, 'Matched', int(uid))
            db.saveUser(int(uid))
            db.saveUser(pid)
            return ConversationHandler.END
        else:
            bot.message.reply_text('Next profile!')
            db.saveUser(int(uid))
            return match(bot, context)
    elif bot.message.text == 'Dislike':
        db.addDislike(int(uid), bot, context)
        db.saveUser(int(uid))
        bot.message.reply_text("Ok :/")
        return match(bot, context)

    else:
        bot.message.reply_text("Invalid input: Please return 'Like', 'Dislike', or 'DONE'.")
        return


def mDone(bot, context):
    bot.message.reply_text('The Blind Cupid has stopped searching for potential partner.')
    return ConversationHandler.END

def matched(bot, context):
    return uHandler.myMatch(db, bot, context)








def message(bot, context):
    uid = str(bot.message.from_user.id)
    user = db.getUser(int(uid))
    
    # Check if there is a match first
    if user['Matched'] == None:
        bot.message.reply_text('You are currently matchless. You can start looking for matches using /match.')
        return ConversationHandler.END
    
    else:
        bot.message.reply_text('Please type your message for your partner.')
        return REPLIES

def reply(bot, context):
    uid = str(bot.message.from_user.id)
    pid = db.getUser(int(uid))['Matched']
    text = bot.message.text
    if text != 'exit':
        context.bot.send_message(pid, ('Match:\n' + text))
        bot.message.reply_text("Message successfully sent! Type 'Exit' if you wish to exit your conversation.")
    # Once user type exit, you stop talking to the match
    else:
        return exit(bot, context)

def exit(bot, context):
    bot.message.reply_text('You have stop messaging your match.')


def remove(bot, context):
    uid = str(bot.message.from_user.id)
    pid = db.getUser(int(uid))['Matched']
    db.updateUser(int(uid), 'Matched', None)
    bot.message.reply_text('You have successfully removed your current match. Type /match to start searching for matches again.')
    db.updateUser(pid, 'Matched', None)
    context.bot.send_message(pid, 'Sorry but your match have decided to remove you.')




def delete(bot, context):
    uid = str(bot.message.from_user.id)
    db.deleteUser(int(uid))
    bot.message.reply_text('Profile successfully removed.')







# The main method to command every method listed above
def main():
    global db
    global uHandler
    global logger
    global valid


    # Intialisation
    botToken = 'INSERT BOT TOKEN HERE'
    db = Database()
    updater = Updater(botToken, use_context=True)
    dp = updater.dispatcher
    uHandler = UserHandler()
    valid = Validator()

    # User Conversation Handler
    uConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('setup', setup)],
        # Second collection: Handlers for conversation
        states = {
            UGENDER: [MessageHandler(Filters.regex('^(Male|Female|)$'), userGender),],
            UAGE: [MessageHandler((Filters.text), userAge),],
            UBIO: [MessageHandler(Filters.regex('^(Height|Weight|Appearance|Year|Major|Faculty' \
                '|Trait 1|Trait 2|Ideal Match|)$'), userBio),],
            UREPLIES: [MessageHandler(Filters.text, userReplies)],
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^DONE$'), uDone)]
    )



    # User Partner Conversation Handler
    pConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('partner', myPartner)],
        # Second collection: Handlers for conversation
        states = {
            PGENDER: [MessageHandler(Filters.regex('^(Male|Female|)$'), partnerGender),],
            PMINAGE: [MessageHandler((Filters.text), partnerMinAge),],
            PMAXAGE: [MessageHandler((Filters.text), partnerMaxAge),]
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^DONE$'), pDone)]
    )

    # Matching Conversation Handler
    mConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('match', match)],
        # Second collection: Handlers for conversation
        states = {
            MCHOICE: [MessageHandler(Filters.regex('^(Like|Dislike|)$'), mChoice),]
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^DONE$'), mDone)]
    )


    # Partner Conversation Handler
    mConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('match', match)],
        # Second collection: Handlers for conversation
        states = {
            MCHOICE: [MessageHandler(Filters.regex('^(Like|Dislike|)$'), mChoice),]
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^DONE$'), mDone)]
    )


    # Partner Conversation Handler
    Convo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('message', message)],
        # Second collection: Handlers for conversation
        states = {
            REPLIES: [MessageHandler((Filters.text), reply),]
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^Exit$'), exit)]
    )





    # Adding all the command handlers
    # Start Commmand
    dp.add_handler(CommandHandler('start', start))
    # Setup Commmand
    dp.add_handler(CommandHandler('profile', userProfile))
    dp.add_handler(uConvo)
    dp.add_handler(pConvo)
    dp.add_handler(mConvo)
    dp.add_handler(Convo)
    dp.add_handler(CommandHandler('message', message))
    dp.add_handler(CommandHandler('delete', delete))
    dp.add_handler(CommandHandler('matched', matched))
    dp.add_handler(CommandHandler('remove', remove))



    # Start the bot
    updater.start_polling()
    updater.idle()
 
if __name__=='__main__':
    main()
