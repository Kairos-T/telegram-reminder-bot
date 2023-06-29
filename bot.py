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

# ===== UPDATE =====

# /set command

"""def set_reminder(update, context):
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

"""


# /set command
def set_reminder(update, context):
    update.message.reply_text("Please enter the name of the event you want to set a reminder for.", reply_markup = reply_markup)
    return NAME

def validate_datetime(datetime_str):
    try:
        datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

def name(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text("Please provide the reminder date & time in the format 'YYYY-MM-DD HH:MM':")

    return DATE_Q

def date_question(update, context):
    if validate_datetime(update.message.text):
        context.user_data['reminder_date_time'] = update.message.text
        update.message.reply_text("Please provide the due date & time in the format 'YYYY-MM-DD HH:MM':")

        return TIME_Q
    else:
        update.message.reply_text("Invalid datetime format. Please provide the reminder date & time in the format 'YYYY-MM-DD HH:MM':")

        return DATE_Q

def time_question(update, context):
    if validate_datetime(update.message.text):
        context.user_data['due_date_time'] = update.message.text

        # Save the reminder
        reminders.append({
            'event_name': context.user_data['name'],
            'reminder_date_time': context.user_data['reminder_date_time'],
            'due_date_time': context.user_data['due_date_time'],
            'chat_id': update.message.chat_id
        })
        save_reminders(reminders)

        update.message.reply_text("Reminder set successfully!")
    else:
        update.message.reply_text("Invalid datetime format. Please provide the due date & time in the format 'YYYY-MM-DD HH:MM':")

        return TIME_Q

# /list command
def list_reminders(update, context):
    chat_id = update.message.chat_id
    user_reminders = [reminder for reminder in reminders if reminder['chat_id'] == chat_id]
    if user_reminders:
        message = "Your reminders:\n"
        for reminder in user_reminders:
            message += f"- {reminder['event_name']} (Reminder: {reminder['reminder_date_time']}, Due: {reminder['due_date_time']})\n"
    else:
        message = "You have no reminders. Use /set to set a reminder! :)"

    update.message.reply_text(message)


# /delete command
def delete_reminder(update, context):
    chat_id = update.message.chat_id
    user_reminders = [reminder for reminder in reminders if reminder['chat_id'] == chat_id]
    if user_reminders:
        buttons = []
        for reminder in user_reminders:
            buttons.append([reminder['event_name']])

        reply_markup = ReplyKeyboardMarkup(buttons)
        update.message.reply_text("Select the reminder you want to delete:", reply_markup=reply_markup)
        return DELETE
    else:
        update.message.reply_text("You have no reminders to delete. :O")


# /delete handler
def delete_handler(update, context):
    selected_event = update.message.text
    chat_id = update.message.chat_id

    user_reminders = [reminder for reminder in reminders if reminder['chat_id'] == chat_id and reminder['event_name'] == selected_event]
    if user_reminders:
        reminders.remove(user_reminders[0])
        save_reminders(reminders)
        update.message.reply_text("Reminder deleted successfully!")
    else:
        update.message.reply_text("Invalid reminder selection.")

    return ConversationHandler.END


# /cancel command
def cancel(update, context):
    update.message.reply_text("Action cancelled!")
    return ConversationHandler.END

# error handlin
def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')


"""
def main():
    # Convo handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set', set_reminder)],
        states={
            NAME: [MessageHandler(Filters.text, name)],
            DATE_Q: [MessageHandler(Filters.text, date_question)],
            TIME_Q: [MessageHandler(Filters.text, time_question)],
            DELETE: [MessageHandler(Filters.text, delete_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    # Handles
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('list', list_reminders))
    dispatcher.add_handler(CommandHandler('delete', delete_reminder))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)

    # Start bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

"""
