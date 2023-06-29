from decouple import Config
import logging
import re
import json
from datetime import datetime
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

config = Config()
config.read_dotenv('.env')
api_token = config.get('API_TOKEN')


def load_reminders():
    try:
        with open('reminders.json', 'r') as f:
            reminders = json.load(f)
    except FileNotFoundError:
        return []
    return reminders

def save_reminders(reminders):
    with open('reminders.json', 'w') as f:
        json.dump(reminders, f, indent=4)

# Load JSON reminders
reminders = load_reminders()

# Convo states
NAME, DATE_Q, TIME_Q, DELETE = range(4)

# /start command
def start(update, context):
    reply_markup = ReplyKeyboardMarkup([['/set', '/list'], ['/delete', '/cancel']])
    update.message.reply_text("Hello! I'm a reminder bot made by @kairostay. What would you like to do? ", reply_markup=reply_markup)

# /set command
def set_reminder(update, context):
    update.message.reply_text("Please enter the name of the event you want to set a reminder for:")
    return NAME

def name(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text("Please provide the reminder date in the format 'YYYY-MM-DD':")
    return DATE_Q

def date_question(update, context):
    user_input = update.message.text.strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', user_input):
        context.user_data['date'] = user_input
        update.message.reply_text("Please provide the reminder time in the format 'HH:MM':")
        return TIME_Q
    else:
        update.message.reply_text("Invalid date format. Please provide the reminder date in the format 'YYYY-MM-DD':")
        return DATE_Q

def time_question(update, context):
    user_input = update.message.text.strip()
    if re.match(r'^\d{2}:\d{2}$', user_input):
        date_str = context.user_data['date']
        time_str = user_input
        reminder_datetime_str = f"{date_str} {time_str}"
        reminder_datetime = datetime.strptime(reminder_datetime_str, '%Y-%m-%d %H:%M')

        # Check if a reminder with the same event name and date/time already exists
        existing_reminder = next((reminder for reminder in reminders
                                  if reminder['event_name'] == context.user_data['name'] and
                                  datetime.fromisoformat(reminder['reminder_datetime']) == reminder_datetime), None)
        if existing_reminder:
            update.message.reply_text("A reminder with the same event name and date/time already exists.")
            return ConversationHandler.END

        reminders.append({
            'event_name': context.user_data['name'],
            'reminder_datetime': reminder_datetime.isoformat(),
            'chat_id': update.message.chat_id
        })
        save_reminders(reminders)

        update.message.reply_text("Reminder set successfully! :D")
    else:
        update.message.reply_text("Invalid time format D: . Please provide the reminder time in the format 'HH:MM':")
        return TIME_Q

# /list command
def list_reminders(update, context):
    chat_id = update.message.chat_id
    user_reminders = [reminder for reminder in reminders if reminder['chat_id'] == chat_id]
    if user_reminders:
        message = "Your reminders:\n"
        for reminder in user_reminders:
            event_name = reminder['event_name']
            reminder_datetime = datetime.fromisoformat(reminder['reminder_datetime'])
            message += f"- {event_name} (Reminder: {reminder_datetime.strftime('%Y-%m-%d %H:%M')})\n"
    else:
        message = "You have no reminders. :("

    update.message.reply_text(message)

# /delete command
def delete_reminder(update, context):
    chat_id = update.message.chat_id
    user_reminders = [reminder for reminder in reminders if reminder['chat_id'] == chat_id]
    if user_reminders:
        buttons = [[reminder['event_name']] for reminder in user_reminders]
        reply_markup = ReplyKeyboardMarkup(buttons)
        update.message.reply_text("Select the reminder you want to delete:", reply_markup=reply_markup)
        return DELETE
    else:
        update.message.reply_text("You have no reminders to delete. :(")

def delete_handler(update, context):
    selected_event = update.message.text
    chat_id = update.message.chat_id
    user_reminders = [reminder for reminder in reminders if reminder['chat_id'] == chat_id and reminder['event_name'] == selected_event]
    if user_reminders:
        reminders.remove(user_reminders[0])
        save_reminders(reminders)
        update.message.reply_text("Reminder deleted successfully!")
    else:
        update.message.reply_text("Invalid reminder selection. :(")

    return ConversationHandler.END

# /cancel command
def cancel(update, context):
    update.message.reply_text("Action cancelled. :( ")
    return ConversationHandler.END

# Error handling
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # convo handler
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

    # dispatcher handles
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('list', list_reminders))
    dispatcher.add_handler(CommandHandler('delete', delete_reminder))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)

    # start
    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    updater = Updater(token=api_token, use_context=True)
    dispatcher = updater.dispatcher
    main()
