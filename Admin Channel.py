from telegram import ReplyKeyboardMarkup
from firebase import firebase
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, \
    PicklePersistence)

BCtoken = 'INSERT BOT TOKEN HERE'
firebase = firebase.FirebaseApplication("https://orbital-2020.firebaseio.com/",None)


# To enable logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Welcome message with a list of commands
def start(update, context):
    update.message.reply_text('Hello! I am the NUS Blind Cupid Bot! ' \
        'I can help you set up a love profile for you to advertise yourself!' \
            '\n\nYou can control me by sending me these commands.' \
                '\n\n/setup - to set up your profile')

# States of dictionary of methods
CHOICES, REPLIES = range(2)

# The keyboard choices to edit your profile
reply_keyboard = [['Gender', 'Age', 'Race'], ['Height', 'Weight', 'Year'], \
    ['Major', 'Faculty'], ['DONE']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# To record the facts given in the bot
def record_facts(user_data):
    facts = list()
    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))
    return "\n".join(facts).join(['\n', '\n'])

# To setup your profile
def setup(update, context):
    update.message.reply_text(
        "To setup your profile, I would like you to fill up some details",
        reply_markup=markup)
    return CHOICES

# The choice a user picked
def choices(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Your {}? Yes, I would love to hear about that!'.format(text.lower()))
    return REPLIES

# The information the user gave so far
def information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']
    update.message.reply_text("Nicely done! This is what you have told me so far:"
                              "\n{} \nYou can tell me more, or edit your current choices."
                              .format(record_facts(user_data)),
                              reply_markup=markup)
    return CHOICES

# The method to END the love profile setup
def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    result = firebase.post('/orbital-2020/admin_channel_data',user_data)
    print(result)
    update.message.reply_text("This is your love profile so far:"
                              "\n{}"
                              "\nUntil next time!".format(record_facts(user_data)))
    user_data.clear()
    return ConversationHandler.END

# To log down the errors caused by updates
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# The main method to command every method listed above
def main():
    # Updater to the Bot
    updater = Updater("1192172658:AAF3I7jtSUySlqSBH5b0kYOiplLmzgwZqqA", use_context=True)
    dp = updater.dispatcher

    # Handles the start method for first time users
    dp.add_handler(CommandHandler('start', start))

    # Converse Method to handle the love profile
    conv_handler = ConversationHandler(
        # First Collection: The command to enter the conversation which is SETUP
        entry_points = [CommandHandler('setup', setup)],

        # Second Collection: The different conversation methods which comprises of a DICT of CHOICES and REPLIES only
        states = {
            CHOICES: [MessageHandler(Filters.regex('^(Gender|Age|Race|Height|Weight|Year|Major|Faculty)$'),
                                      choices),
                            ],
            REPLIES: [MessageHandler(Filters.text,
                                          information),
                           ],
        },

        # Third Collection: The command to exit the conversation
        fallbacks=[MessageHandler(Filters.regex('^DONE$'), done)]

    )
    # To add the conversation handler above
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    #upload the data to firebase


    updater.idle()

if __name__=='__main__':
    main()
