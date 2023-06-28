import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re
import datetime
import json


# Initialise Bot
'''
updater = Updater(token='API TOKEN', use_context=True)
dispatcher = updater.dispatcher
'''

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
