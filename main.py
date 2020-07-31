import threading, time
import yaml
from database import Database
from userhandler import UserHandler
from validator import Validator
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler



# Dict for conversation handlers
UTOPIC, UGENDER, UAGE, UREPLIES, UREMOVE, PTOPIC, PGENDER, PMINAGE, PMAXAGE, MCHOICE, REPLIES, RCHOICE, DCHOICE, ECHOICE = range(14)



# START COMMAND
def start(bot, context):
    return uHandler.start(db, bot, context)



# CONVERSATION HANDLING PART 1: USER PROFILE
# SETUP COMMAND
def setup(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    cid = bot.message.chat_id
    username = bot.message.from_user.username
    # Check username
    if username == None:
        bot.message.reply_text(lang['register'])
        return ConversationHandler.END
    # Check if user in database
    if user == None:
        db.addUser(uid, cid, username)
        bot.message.reply_text(lang['setup'], reply_markup=uHandler.markup['userBIO'])
        return UTOPIC
    # Recurring user
    else:
        userBIO = db.sortProfile(uid)
        bot.message.reply_text('This is your current profile.\n' + userBIO + \
            '\nWhat would you like to edit?', reply_markup=uHandler.markup['userBIO'])
        return UTOPIC

# To handle user topic choice after setup
def userTopic(bot, context):
    uid = bot.message.from_user.id
    otherTopic = ['Height', 'Weight', 'Appearance', 'Year', 'Major', 'Faculty', 'Trait 1', 'Trait 2', 'Ideal Match']
    topic = bot.message.text
    context.user_data['choice'] = topic
    # If topic is gender
    if topic == 'Gender':
        if context.user_data.get(topic):
            bot.message.reply_text('Your stated gender is currently {}. ' \
                'What would you like to change it to?'.format(context.user_data[topic]), reply_markup=uHandler.markup['userGender'])
        else:
            bot.message.reply_text(lang['userGender'], reply_markup=uHandler.markup['userGender'])
        return UGENDER
    # If topic is age
    elif topic == 'Age':
        if context.user_data.get(topic):
            bot.message.reply_text('Your stated age is currently {}. ' \
                'What would you like to change it to?'.format(context.user_data[topic]))
        else:
            bot.message.reply_text(lang['userAge'])
        return UAGE
    # If user wish to remove a trait
    elif topic == 'Remove':
        bot.message.reply_text(lang['userRemove'], reply_markup=uHandler.markup['userBIO2'])
        return UREMOVE
    # Rest of the topics
    elif topic == 'Done':
        return uDone(bot, context)
    # Rest of the topics
    elif topic in otherTopic:
        if context.user_data.get(topic):
            bot.message.reply_text('Your {} is currently {}. What would you like to change it to?'.format(topic.lower(), context.user_data[topic].lower()))
        else:
            bot.message.reply_text('Your {}? Yes I would love to hear about that!'.format(topic.lower()))
        return UREPLIES
    # Invalid user topic
    else:
        bot.message.reply_text(lang['userTopicInvalid'], reply_markup=uHandler.markup['userBIO'])
        return

# When USER topic is GENDER
def userGender(bot, context):
    uid = bot.message.from_user.id
    topic = context.user_data['choice']
    answer = bot.message.text
    context.user_data[topic] = answer.lower()
    # Filter the user gender accordingly
    if answer == 'Male':
        db.updateUser(uid, 'Gender', 'Male')
    elif answer == 'Female':
        db.updateUser(uid, 'Gender', 'Female')
    else:
        bot.message.reply_text(lang['userGenderInvalid'])
        return
    bot.message.reply_text(lang['setupSTD'], reply_markup=uHandler.markup['userBIO'])
    del context.user_data['choice']
    return UTOPIC

# When USER topic is GENDER
def userAge(bot, context):
    uid = bot.message.from_user.id
    topic = context.user_data['choice']
    answer = bot.message.text
    context.user_data[topic] = answer
    # Check for valid age
    if valid.validAge(answer):
        db.updateUser(uid, 'Age', int(answer))
        bot.message.reply_text(lang['setupSTD'], reply_markup=uHandler.markup['userBIO'])
        del context.user_data['choice']
        return UTOPIC
    else:
        bot.message.reply_text(lang['userAgeInvalid'])
        return

# When USER topic is OTHER
def userReplies(bot, context):
    uid = bot.message.from_user.id
    topic = context.user_data['choice']
    answer = bot.message.text
    db.updateUser(uid, topic, answer)
    context.user_data[topic] = answer.lower()
    bot.message.reply_text(lang['setupSTD'], reply_markup=uHandler.markup['userBIO'])
    del context.user_data['choice']              
    return UTOPIC

# When USER topic is REMOVE
def userRemove(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    rTopic = bot.message.text
    removeTopic = ['Gender', 'Age', 'Height', 'Weight', 'Appearance', 'Year', 'Major', 'Faculty', 'Trait 1', 'Trait 2', 'Ideal Match']
    # Check if topic chosen is valid
    if rTopic in removeTopic:
        if rTopic in user.keys():
            db.deleteTrait(uid, rTopic)
            bot.message.reply_text(lang['userRemovedPass'])
        else:
            bot.message.reply_text(lang['userRemoveFail'])
        sortedProfile = db.sortProfile(uid)
        bot.message.reply_text(sortedProfile + '\nAny other trait that you wish to remove?', reply_markup=uHandler.markup['userBIO2'])
        return UREMOVE
    elif rTopic == 'Done':
        sortedProfile = db.sortProfile(uid)
        bot.message.reply_text(sortedProfile + '\nAny other changes to your profile?', reply_markup=uHandler.markup['userBIO'])
        return UTOPIC
    else:
        bot.message.reply_text(lang['userRemoveInvalid'], reply_markup=uHandler.markup['userBIO2'] )
        return

# When USER topic is DONE
def uDone(bot, context):
    uid = bot.message.from_user.id
    if 'choice' in context.user_data:
        del context.user_data['choice']
    userBIO = db.sortProfile(uid)
    bot.message.reply_text('This is your profile so far.\n' + userBIO + '\nType /setup if you wish to edit again. '\
        'Otherwise, type /criteria to specify your ideal match.')
    return ConversationHandler.END



# PROFILE COMMAND
def userProfile(bot, context):
    return uHandler.userBIO(db, bot, context)



# CONVERSATION HANDLING PART 2: PARTNER CRITERIA
# CRITERIA COMMAND
def partnerSetup(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    if user == None:
        bot.message.reply_text(lang['noProfile'])
        return ConversationHandler.END
    # First time setup for criteria
    elif 'partnerGender' not in user or 'partnerMinAge' not in user or 'partnerMaxAge' not in user:
        bot.message.reply_text(lang['noCriteria'], reply_markup=uHandler.markup['partnerBIO'])
    # Criteria setup before
    else:
        partnerBIO = db.sortPartner(uid)
        bot.message.reply_text('This is your current criteria for your match.\n' + partnerBIO + \
            '\nWhat would you like to edit?', reply_markup=uHandler.markup['partnerBIO'])
    return PTOPIC

# To handle partner topic choice after criteria
def partnerTopic(bot, context):
    uid = bot.message.from_user.id
    ptopic = bot.message.text
    context.user_data['pchoice'] = ptopic
    # When PARTNER topic is GENDER
    if ptopic == 'Partner Gender':
        if context.user_data.get(ptopic):
            bot.message.reply_text('Your current ideal partner gender is {}. '\
                'What would you like to change it to?'.format(context.user_data[ptopic]), \
                    reply_markup=uHandler.markup['partnerGender'])
        else:
            bot.message.reply_text('Your ideal partner gender? Yes I would love to hear about that!', reply_markup=uHandler.markup['partnerGender'])
        return PGENDER
    # When PARTNER topic is MINIMUM AGE
    elif ptopic == 'Minimum Age':
        if context.user_data.get(ptopic):
            bot.message.reply_text('Your current ideal partner minimum age is {}. '\
                'What would you like to change it to?'.format(context.user_data[ptopic]))
        else:
            bot.message.reply_text('Your ideal partner minimum age? Yes I would love to hear about that!')
        return PMINAGE
    # When PARTNER topic is MAXIMUM AGE
    elif ptopic == 'Maximum Age':
        if context.user_data.get(ptopic):
            bot.message.reply_text('Your current ideal partner maximum age is {}. '\
                'What would you like to change it to?'.format(context.user_data[ptopic]))
        else:
            bot.message.reply_text('Your ideal partner maximum age? Yes I would love to hear about that!')
        return PMAXAGE
    # When PARTNER topic is DONE
    elif ptopic == 'Done':
        return pDone(bot, context)
    # Invalid partner topic
    else:
        bot.message.reply_text(lang['pTopicInvalid'], reply_markup=uHandler.markup['partnerBIO'])
        return

# When PARTNER topic is GENDER
def partnerGender(bot, context):
    uid = bot.message.from_user.id
    ptopic = context.user_data['pchoice']
    panswer = bot.message.text
    context.user_data[ptopic] = panswer.lower()
    # Handles partner gender accordingly
    if panswer == 'Male':
        db.updateUser(uid, 'partnerGender', panswer)
    elif panswer == 'Female':
        db.updateUser(uid, 'partnerGender', panswer)
    elif panswer == 'Both':
        db.updateUser(uid, 'partnerGender', panswer)
    else:
        bot.message.reply_text(lang['pGenderInvalid'], reply_markup=uHandler.markup['partnerGender'])
        return
    del context.user_data['pchoice']
    bot.message.reply_text(lang['criteriaSTD'], reply_markup=uHandler.markup['partnerBIO'])
    return PTOPIC

# When PARTNER topic is MINIMUM AGE
def partnerMinAge(bot, context):
    uid = bot.message.from_user.id
    ptopic = context.user_data['pchoice']
    panswer = bot.message.text
    context.user_data[ptopic] = panswer
    # Check for valid integer given
    if valid.validAge(panswer):
        db.updateUser(uid, 'partnerMinAge', int(panswer))
        del context.user_data['pchoice']
        bot.message.reply_text(lang['criteriaSTD'], reply_markup=uHandler.markup['partnerBIO'])
        return PTOPIC
    else:
        bot.message.reply_text(lang['pAgeInvalid'])
        return

# When PARTNER topic is MINIMUM AGE
def partnerMaxAge(bot, context):
    uid = bot.message.from_user.id
    ptopic = context.user_data['pchoice']
    panswer = bot.message.text
    context.user_data[ptopic] = panswer
    # Check valid integer given
    if valid.validAge(panswer):
        db.updateUser(uid, 'partnerMaxAge', int(panswer))
        del context.user_data['pchoice']
        bot.message.reply_text(lang['criteriaSTD'], reply_markup=uHandler.markup['partnerBIO'])
        return PTOPIC
    else:
        bot.message.reply_text(lang['pAgeInvalid'])
        return

# When PARTNER topic is DONE
def pDone(bot, context):
    uid = bot.message.from_user.id
    if 'pchoice' in context.user_data:
        del context.user_data['pchoice']
    partnerBIO = db.sortPartner(uid)
    bot.message.reply_text('This is your partner criteria.\n' + partnerBIO + '\nType /criteria if you wish to edit again. ' \
        'Otherwise, type /match to start looking for profiles.')
    return ConversationHandler.END



# CONVERSATION HANDLING PART 3: MATCH 
def match(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    if user == None:
        bot.message.reply_text(lang['noProfile'])
        return ConversationHandler.END
    # Check user profile key information are given
    if valid.checkUserMatchReady(user) == False:
        bot.message.reply_text(lang['mSetupInvalid'])
        return ConversationHandler.END
    # Check user partner criteria key information are given
    elif valid.checkPartnerMatchReady(user) == False:
        bot.message.reply_text(lang['mPartnerInvalid'])
        return ConversationHandler.END
    # When user has no expired partner
    elif user['Matched'] == 'None' and user['userExchange'] != "None":
        bot.message.reply_text(lang['mExchangeInvalid'])
        return ConversationHandler.END
    # When user can match
    else:
        # When user has no partner
        if user['Matched'] == 'None':
            # Start finding potential matches
            for i in db.allProfiles():
                if valid.checkPartner(user, db.allProfiles()[i]):
                    partner = db.allProfiles()[i]
                    db.updateUser(uid, 'lastProfile', partner['id'])
                    partnerProfile = db.sortProfile(partner['id'])
                    bot.message.reply_text("Here's a profile:\n" + partnerProfile, \
                        reply_markup=uHandler.markup['matchChoice'])
                    return MCHOICE
            # When there is no more partner for user
            bot.message.reply_text(lang['mNoPartner'])
            return ConversationHandler.END
        # If user has a partner
        else:
            pid = user['Matched']
            partnerBIO = db.sortProfile(pid)
            bot.message.reply_text(partnerBIO + lang['gotPartner'])
            return ConversationHandler.END

# User indication for each potential profile
def mChoice(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    pid = db.getUser(uid)['lastProfile']
    partner = db.getUser(pid)
    mchoice = bot.message.text
    # User dislike
    if mchoice == 'Dislike':
        db.addDislike(uid, pid)
        bot.message.reply_text(lang['mDislike'])
        return match(bot, context)
    # User like
    elif mchoice == 'Like':
        db.addLike(uid, pid)
        mutually = valid.checkMatch(uid, pid)
        # Check if partner likes you too
        if mutually == True:
            bot.message.reply_text(lang['mLikeUser'])
            context.bot.send_message(pid, (lang['mLikePartner']))
            db.updateUser(uid, 'Matched', pid)
            db.updateUser(pid, 'Matched', uid)
            db.updateUser(uid, 'userExchange', pid)
            db.updateUser(pid, 'userExchange', uid)
            # Start the countdown
            countdown = threading.Thread(target = matchedLife, args=(bot, context, uid, pid))
            countdown.start()
            return ConversationHandler.END
        # When partner does/has not like user
        else:
            bot.message.reply_text('Next profile!')
            return match(bot, context)
    # If stop searching
    elif mchoice == 'Done':
        return mDone(bot, context)
    else:
        bot.message.reply_text(lang['mInvalid'])
        return
# When user stop searching for partner
def mDone(bot, context):
    bot.message.reply_text(lang['mDone'])
    return ConversationHandler.END



# Handles the matched partner profile
def partner(bot, context):
    return uHandler.myPartner(db, bot, context)



# CONVERSATION HANDLING PART 4: Matched Partner Conversation
def message(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    if user == None:
        bot.message.reply_text(lang['noProfile'])
        return ConversationHandler.END
    # When user is no longer matched
    elif user['Matched'] == 'None':
        if user['userExchange'] == 'None':
            bot.message.reply_text(lang['meNoMatch'])
        else:
            bot.message.reply_text(lang['meExpiredMatch'])
        return ConversationHandler.END
    # When user has a matched partner
    else:
        bot.message.reply_text(lang['meMatchPass'])
        return REPLIES

def reply(bot, context):
    uid = bot.message.from_user.id
    pid = db.getUser(uid)['Matched']
    # Handles all form of messages to be sent that I could think of
    item = bot.message.text or bot.message.sticker or bot.message.animation or bot.message.photo or bot.message.audio \
        or bot.message.video or bot.message.voice or bot.message.document or bot.message.location \
             or bot.message.contact or bot.message.poll
    # To filter all kind of messages sent
    if item == bot.message.text:
        if item == 'Exit':
            return exit(bot, context)
        else:
            context.bot.send_message(pid, 'Match:\n\n' + item)
    elif item == bot.message.sticker:
        context.bot.send_sticker(pid, item)
    elif item == bot.message.animation:
        context.bot.send_animation(pid, item)
    elif item == bot.message.photo:
        context.bot.send_photo(pid, item[-1])
    elif item == bot.message.audio:
        context.bot.send_audio(pid, item)
    elif item == bot.message.video:
        context.bot.send_video(pid, item)
    elif item == bot.message.voice:
        context.bot.send_voice(pid, item)
    elif item == bot.message.document:
        context.bot.send_document(pid, item)
    elif item == bot.message.location:
        latitude = bot.message.location['latitude']
        longitude = bot.message.location['longitude']
        context.bot.send_location(pid, latitude, longitude)
    elif item == bot.message.contact:
        pNumber = item['phone_number']
        firstName = item['first_name']
        lastName = item['last_name']
        context.bot.send_contact(pid, pNumber, firstName, lastName)
    # Polling possibility
    elif item == bot.message.poll:
        bot.message.reply_text(lang['meNoPoll'])
        return
    # Incase telegram can send more kind of items listed
    else:
        bot.message.reply_text(lang['meInvalid'])
        return
    # Valid item
    bot.message.reply_text(lang['mePass'])

# When user exit the MESSAGE COMMAND
def exit(bot, context):
    bot.message.reply_text(lang['meExit'])
    return ConversationHandler.END



# CONVERSATION HANDLING PART 5:ELIMINATION (REMOVE & DELETE) COMMAND
# REMOVE PARTNER COMMAND
def remove(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    # No profile
    if user == None:
        bot.message.reply_text(lang['noProfile'])
        return ConversationHandler.END
    # No match
    elif user['Matched'] == 'None':
        # Got Exchange
        if user['userExchange'] != 'None':
            pid = user['userExchange']
            partnerBIO = db.sortProfile(pid)
            bot.message.reply_text(partnerBIO + lang['reCfmExp'], reply_markup=uHandler.markup['confirmation'])
            return RCHOICE
        # No Exchange
        else:
            bot.message.reply_text(lang['noPartner'])
            return ConversationHandler.END
    # Got match
    else:
        pid = user['Matched']
        partnerBIO = db.sortProfile(pid)
        bot.message.reply_text(partnerBIO + lang['reCfm'], reply_markup=uHandler.markup['confirmation'])
        return RCHOICE

# User Removal Choice
def removeChoice(bot, context):
    uid = bot.message.from_user.id
    confirmation = bot.message.text
    # To remove partner
    if confirmation == 'Yes':
        pid = db.getUser(uid)['Matched']
        db.updateUser(uid, 'Matched', 'None')
        db.updateUser(uid, 'userExchange', 'None')
        bot.message.reply_text(lang['reUserPass'])
        db.updateUser(pid, 'Matched', 'None')
        db.updateUser(pid, 'userExchange', 'None')
        context.bot.send_message(pid, lang['rePartnerPass'])
    # Stop removal
    elif confirmation == 'No':
        bot.message.reply_text(lang['reFail'])
    else:
        bot.message.reply_text(lang['reInvalid'])
        return
    return ConversationHandler.END

# DELETE COMMAND
def delete(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    if user == None:
        bot.message.reply_text(lang['noProfile'])
        return ConversationHandler.END
    else:
        bot.message.reply_text(lang['deCfm'], reply_markup=uHandler.markup['confirmation'])
        return DCHOICE

# Delete Choice
def deleteChoice(bot, context):
    uid = bot.message.from_user.id
    confirmation = bot.message.text
    user = db.getUser(uid)
    # To delete
    if confirmation == 'Yes':
        # When user delete with a matched partner
        if user['Matched'] != 'None':
            pid = user['Matched']
            db.updateUser(pid, 'Matched', 'None')
            db.updateUser(pid, 'userExchange', 'None')
            context.bot.send_message(pid, lang['dePartnerPass'])
        # Stream through other profiles in Database to delete user id
        for i in db.allProfiles():
            oid = db.allProfiles()[i]['id']
            if str(uid) in db.allProfiles()[i]['Likes']:
                db.deleteUserLikes(oid, uid)
            if str(uid) in db.allProfiles()[i]['Dislikes']:
                db.deleteUserDislikes(oid, uid)
        db.deleteUser(uid)
        bot.message.reply_text(lang['deUserPass'])
    elif confirmation == 'No':
        bot.message.reply_text(lang['deFail'])
    else:
        bot.message.reply_text(lang['deInvalid'])
        return
    return ConversationHandler.END



# HELP COMMAND
def help(bot, context):
    return uHandler.help(bot, context)



# COUNTDOWN TIMER
def matchedLife(bot, context, uid, pid):
    # 1 Week lifespan
    t = 604800
    while t > 0:
        t -= 3600
        time.sleep(3600)
        # Scan to end countdown whenever required HELLLLLLLLLLLLLLLLLLLLLLLLPPPPPPPPPPP KILLLLL THREAD see REMOVE AND DELETE
        if db.getUser(uid)['Matched'] == 'None':
            return ConversationHandler.END
    # End of countdown
    db.updateUser(uid, 'Matched', 'None')
    db.updateUser(pid, 'Matched', 'None')
    context.bot.send_message(uid, lang['cd'])
    context.bot.send_message(pid, lang['cd'])
    return ConversationHandler.END




# CONVERSATION HANDLING PART 6: EXCHANGE COMMAND
def exchange(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    # Check profile
    if user == None:
        bot.message.reply_text(lang['noProfile'])
        return ConversationHandler.END
    # Check match
    elif user['userExchange'] == 'None':
        bot.message.reply_text(lang['noPartner'])
        return ConversationHandler.END
    # Existing match
    else:
        pid = user['userExchange']
        partnerBIO = db.sortProfile(pid)
        bot.message.reply_text(partnerBIO + lang['exCfm'],  \
                reply_markup=uHandler.markup['exchange'])
        return ECHOICE

# Exchange Choice
def exchangeChoice(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    pid = db.getUser(uid)['userExchange']
    partner = db.getUser(pid)
    decision = bot.message.text
    # To exchange
    if decision == 'Accept':
        db.updateUser(uid, 'userExchange', 'Accept')
        mutually = valid.checkExchange(pid)
        # Mutual exchange
        if mutually == 1:
            uHandler = user['username']
            pHandler = partner['username']
            # Send user
            bot.message.reply_text(lang['exPass'])
            # User suspense
            time.sleep(1)
            bot.message.reply_text('.')
            time.sleep(1)
            bot.message.reply_text('..')
            time.sleep(1)
            bot.message.reply_text('...')
            time.sleep(1)
            bot.message.reply_text(pHandler)
            # Send Partner
            context.bot.send_message(pid, lang['exPass'])
            # Partner suspense
            time.sleep(1)
            context.bot.send_message(pid, '.')
            time.sleep(1)
            context.bot.send_message(pid, '..')
            time.sleep(1)
            context.bot.send_message(pid, '...')
            time.sleep(1)
            context.bot.send_message(pid, uHandler)
            # Update accordingly
            db.updateUser(uid, 'Matched', 'None')
            db.updateUser(uid, 'userExchange', 'None')
            db.updateUser(pid, 'Matched', 'None')
            db.updateUser(pid, 'userExchange', 'None')
        # Partner yet to respond
        elif mutually == 2:
            bot.message.reply_text(lang['exUserWait'])
            context.bot.send_message(pid, lang['exPartnerWait'])
        return ConversationHandler.END
    # Reject Exchange
    elif decision == 'Reject':
        bot.message.reply_text(lang['exUserFail'])
        context.bot.send_message(pid, lang['exPartnerFail'])
        db.updateUser(uid, 'Matched', 'None')
        db.updateUser(uid, 'userExchange', 'None')
        db.updateUser(pid, 'Matched', 'None')
        db.updateUser(pid, 'userExchange', 'None')
        return ConversationHandler.END
    # Cancel Exchange
    elif decision == 'Cancel':
        return exchangeCancel(bot, context)
    # Invalid exchange
    else:
        bot.message.reply_text(lang['exInvalid'])
        return

# Handles Cancellation of exchange command
def exchangeCancel(bot, context):
    uid = bot.message.from_user.id
    user = db.getUser(uid)
    # Prompt user to act if its a case of expired partner
    if user['Matched'] == 'None':
        bot.message.reply_text(lang['exExpCancel'])
    # Normal cancellation
    else:
        bot.message.reply_text(lang['exCancel'])
    return ConversationHandler.END



# EASTER EGGS
def easterCG(bot,context):
    bot.message.reply_text(lang['CG'])
def easterKG(bot, context):
    bot.message.reply_text(lang['KG'])



# The main method to command every method listed above
def main():
    global db
    global uHandler
    global valid
    global lang
 
    # Intialisation
    botToken = 'INSERT BOT TOKEN HERE'
    updater = Updater(botToken, use_context=True)
    botLang = open("lang.yml", 'r')
    lang = yaml.load(botLang, Loader=yaml.SafeLoader)
    uHandler = UserHandler(lang)
    dp = updater.dispatcher
    db = Database()
    valid = Validator()

    # CONVERSATION PART 1: User Conversation Handler
    uConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('setup', setup)],
        # Second collection: Handlers for conversation
        states = {
            UTOPIC: [MessageHandler(Filters.text, userTopic),],
            UGENDER: [MessageHandler(Filters.text, userGender),],
            UAGE: [MessageHandler(Filters.text, userAge),],
            UREPLIES: [MessageHandler(Filters.text, userReplies),],
            UREMOVE: [MessageHandler(Filters.text, userRemove),]
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^Done$'), uDone)]
    )

    # CONVERSATION PART 2: User Partner Conversation Handler
    pConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('criteria', partnerSetup)],
        # Second collection: Handlers for conversation
        states = {
            PTOPIC: [MessageHandler(Filters.text,partnerTopic),],
            PGENDER: [MessageHandler(Filters.text, partnerGender),],
            PMINAGE: [MessageHandler(Filters.text, partnerMinAge),],
            PMAXAGE: [MessageHandler(Filters.text, partnerMaxAge)]
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^Done$'), pDone)]
    )

    # CONVERSATION PART 3: Matching Conversation Handler
    mConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('match', match)],
        # Second collection: Handlers for conversation
        states = {
            MCHOICE: [MessageHandler(Filters.text, mChoice)]
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^Done$'), mDone)]
        )

    # CONVERSATION PART 4: Partner Message Conversation
    Convo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('message', message)],
        # Second collection: Handlers for conversation
        states = {
            REPLIES: [MessageHandler((Filters.all), reply),],
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^Exit$'), exit)]
    )

    # CONVERSATION PART 5: Elimination (Remove & Delete) Conversation
    dConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('remove', remove), CommandHandler('delete', delete)],
        # Second collection: Handlers for conversation
        states = {
            RCHOICE: [MessageHandler(Filters.text, removeChoice),],
            DCHOICE: [MessageHandler(Filters.text, deleteChoice),]
        },
        # Third Collection: Exit the conversation
        fallbacks = []
    )

    # CONVERSATION PART 6: Exchange username
    eConvo = ConversationHandler(
        # First collection: Entry to conversation
        entry_points = [CommandHandler('exchange', exchange)],
        # Second collection: Handlers for conversation
        states = {
            ECHOICE: [MessageHandler((Filters.text), exchangeChoice)]
        },
        # Third Collection: Exit the conversation
        fallbacks = [MessageHandler(Filters.regex('^Cancel$'), exchangeCancel)]
    )

    # Adding all the command handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('profile', userProfile))
    dp.add_handler(uConvo)
    dp.add_handler(pConvo)
    dp.add_handler(mConvo)
    dp.add_handler(Convo)
    dp.add_handler(CommandHandler('partner', partner))
    dp.add_handler(dConvo)
    dp.add_handler(eConvo)
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.regex('^LCG$'), easterCG))
    dp.add_handler(MessageHandler(Filters.regex('^CKG$'), easterKG))
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()