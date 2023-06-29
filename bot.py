import logging
import re
import json
from datetime import datetime, timedelta
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_reminders():
    try:
        with open('reminders.json', 'r') as f:
            reminders = json.load(f)

    except FileNotFoundError:
        return []
    return reminders

# Load JSON reminders
reminders = load_reminders()

# Saving reminders
def save_reminders(reminders):
    with open('reminders.json', 'w') as f:
        json.dump(reminders, f, indent=4)

# Initialise Bot
'''
updater = Updater(token='API TOKEN', use_context=True)
dispatcher = updater.dispatcher
'''

# Convo states
NAME, DATE_Q, TIME_Q, INFO, OPT, DELETE = range(6)
UTC_1, UTC_2 = range(2)

# /start command
def start(update, context):
    reply_markup = ReplyKeyboardMarkup([['/set', '/list'], ['/delete', '/cancel']])
    update.message.reply_text("Hello! I'm a reminder bot created by @kairostay. What would you like to do?", reply_markup=reply_markup)



# /set command
def set_reminder(update, context):
    user_input = update.message.text[5:]
    pattern = r'(.+?)(.+?)(.+?)'
    match = re.match(pattern, user_input)

    if match:
        event_name = match.group(1)
        reminder_date_time = match.group(2)
        due_date_time = match.group(3)

        reminders.append({
            'event_name': event_name,
            'reminder_date_time': reminder_date_time,
            'due_date_time': due_date_time,
            'chat_id': update.message.chat_id
        })

        save_reminders(reminders)

        update.message.reply_text("Reminder set successfully!")
    else:
        update.message.reply_text("Invalid command format. Please use '/set <event name> <reminder date & time> <due date & time>'")
