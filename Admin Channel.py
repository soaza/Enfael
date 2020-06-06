from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, PicklePersistence)
 
BCtoken = '1192172658:AAF3I7jtSUySlqSBH5b0kYOiplLmzgwZqqA'
 
# To enable logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Welcome message with a list of commands
def start(update, context):
    update.message.reply_text('Hello! I am the NUS Blind Cupid Bot! ' \
        'I can help you set up a love profile for you to advertise yourself and hopefully find a match!' \
            '\n\nYou can control me by sending me these commands.' \
                '\n\n/setup - to set up your profile\n/myprofile - to see your profile' \
                    '\n/publicise - to publicise your profile')
 
# States of dictionary of methods
CHOICES, REPLIES = range(2)
 
# The keyboard choices to edit your profile
reply_keyboard = [['Gender', 'Age', 'Race'], ['Height', 'Weight', 'Appearance'], \
    ['Year', 'Major', 'Faculty',], ['Trait 1', 'Trait 2', 'Ideal Match'], ['DONE']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
 
# To record the facts given in the bot
def record_facts(user_data):
    facts = list()
    for key, value in user_data.items():
        facts.append('{}: {}'.format(key, value))
    return "\n".join(facts).join(['\n', '\n'])

# To setup your profile
def setup(update, context):
    reply = "To setup your profile, I would like you to fill up some details."
    # When you setup before
    if context.user_data:
        reply += ' You have already told me your {}. Would you like to tell me more'\
            ' or edit any of your existing choice(s)?'.format(", ".join(context.user_data.keys()))
    # First time setup
    else:
        reply += " Do keep your details short and sweet!"
    update.message.reply_text(reply, reply_markup=markup)
    return CHOICES

# The choice a user picked
def choices(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    # When at least one choice has been made before
    if context.user_data.get(text):
        reply = 'Your {}, I already know the following about that: {}'.format(text.lower(), context.user_data[text])
    # First time picking that choice
    else:
        reply = 'Your {}? Yes, I would love to hear about that!'.format(text.lower())
    update.message.reply_text(reply)
    return REPLIES
 
# The information the user gave so far
def information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']
    update.message.reply_text("Nicely done! This is what you have told me so far:"
                              "\n{} \nYou can tell me more, edit them, or choose done to complete your profile."
                              .format(record_facts(user_data)), reply_markup=markup)
    return CHOICES

def myprofile(update, context):
    update.message.reply_text("This is what you have told me so far:"
                              "{}".format(record_facts(context.user_data)))

# To exit the conversation handling of setting up your love profile
def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    update.message.reply_text("This is your love profile so far:"
                              "\n{}"
                              "\nIf you are ready, you can publicise it using /publicise".format(record_facts(user_data)))
    return ConversationHandler.END

# To log down the errors caused by updates
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# The main method to command every method listed above
def main():
    # Persistence, Updater and Dispatcher of the Bot
    pp = PicklePersistence(filename='UserData')
    updater = Updater(BCtoken, persistence = pp, use_context=True)
    dp = updater.dispatcher
 
    # Handles the start method for first time users
    dp.add_handler(CommandHandler('start', start))
 
    # Converse Method to handle the love profile
    conv_handler = ConversationHandler(
        # First Collection: The command to enter the conversation which is SETUP
        entry_points = [CommandHandler('setup', setup)],
 
        # Second Collection: The different conversation methods which comprises of a DICT of CHOICES and REPLIES only
        states = {
            CHOICES: [MessageHandler(Filters.regex('^(Gender|Age|Race|Height|Weight|Appearance|Year|Major|Faculty' \
                '|Trait 1|Trait 2|Ideal Match|)$'), choices),],
            REPLIES: [MessageHandler(Filters.text, information),],
        },
 
        # Third Collection: The command to exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^DONE$'), done)],
        name = "SetupData",
        persistent = True
    )
    # To add the conversation handler above
    dp.add_handler(conv_handler)
 
    # To add the handler for user to see their existing love profile
    dp.add_handler(CommandHandler('myprofile', myprofile))

    # log all errors
    dp.add_error_handler(error)
 
    # Start the bot
    updater.start_polling()
 
    # To stop the Bot by pressing Ctrl+C or sending a signal to the Bot process
    updater.idle()
 
if __name__=='__main__':
    main()
