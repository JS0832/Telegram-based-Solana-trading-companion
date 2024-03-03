from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Replace 'YOUR_TOKEN' with your actual bot token
TOKEN = 'YOUR_TOKEN'

# Define the list of chat IDs of users you want to send the message to
user_chat_ids = [123456789, 987654321]  # Add your users' chat IDs here

# Define the message you want to send
message_text = "Hello! This is a customizable message."

# Define the inline keyboard
inline_keyboard = [
    [InlineKeyboardButton("Button 1", callback_data="btn1"), InlineKeyboardButton("Button 2", callback_data="btn2")]
]

keyboard_markup = InlineKeyboardMarkup(inline_keyboard)


def send_message_to_users(update: Update, context: CallbackContext):
    for chat_id in user_chat_ids:
        context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=keyboard_markup)


def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Button pressed: {query.data}")


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Add command handler to trigger sending message to users
    dispatcher.add_handler(CommandHandler("send_message", send_message_to_users))

    # Add callback handler to handle button presses
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

