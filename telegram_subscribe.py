import time
from helius import TransactionsAPI
from functools import reduce
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import final

BOT_USERNAME: final = '@subOnSolbot'
BOT_TOKEN = "7089696589:AAGA2jbfzBgmixtmf4X8I4ZRlZ5mdnAp5zk"

# check if the main wallet has been credited by the address provided with the right amount of sol coins
# place on queue and wait maybe 2h for it to be credited if 2h passed ping the user that purchase was unuseful and they have to retry
sub_queue = []  # [telegram tag,time of applying,wallet provided] #if there is a 1sol purchase between the application time and now then add to sub list and remove from queue else remove form eueu and ping the user
# our main wallet DzoUHyo6jaEypWYyKSmhAiZmxcpjXuTNhXEyXmGWxHZ3
sub_list = []  # will have file backups but also keep most in memory to ensure speed
transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "welcome incel,plase enter the wallet address you will be sending the funds from and also the package type.you can enter the infomration in any order you wish as long as they are seperate messages."
        "enter 1 for 1 month ,2 for 3 months and 3 for lifetime")
    await update.message.reply_text("sedn funds here : DzoUHyo6jaEypWYyKSmhAiZmxcpjXuTNhXEyXmGWxHZ3")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = str(update.effective_user)
    add_to_queue(name, "", -1)
    text = update.message.text
    result = handle_input(text)
    temp_index = 0
    for user in sub_queue:
        if user[0] == name:
            break  # helps to figure out the index of the user
        temp_index += 1
    if result == -1:  # amount
        sub_queue[temp_index][2] = int(text)
    elif result == 1:
        sub_queue[temp_index][1] = str(text)
    await update.message.reply_text(
        "reminder: thank you for providing the info,once the bot detects all info is provided you will recieve a confirmation after the pruchase is complete")


def handle_input(text):  # -1 is amount and 1 is address
    if text == "1":
        return -1
    elif text == "2":
        return -1
    elif text == "3":
        return -1
    elif len(text) == len("5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g"):
        return 1


def append_user_to_database():
    while True:
        if len(sub_list) > 0:
            with open('subscribers.txt', 'a') as file:
                file.write(str(sub_list[0]) + '\n')
                sub_list.pop(0)


# needs to check if a wallet already exists,if user is already registered,if they are then it neds to send
# confirmation for upgrade?

async def check_queue():
    expiration_time = 3600
    while True:
        if len(sub_queue) > 0:
            index = 0
            for user in sub_queue:
                expected_sol = 0
                # first check then remove if timestamp is > current time
                if user[2] == 0:  # monthly (0.4 sol)
                    expected_sol = 0.4
                elif user[2] == 1:  # 3-month (1 sol)
                    expected_sol = 1
                elif user[2] == 2:  # lifetime (3 sol)
                    expected_sol = 3
                if verify_tx(user[1], expected_sol):  # passed
                    # try to send confirmation to the users id maybe?
                    # add the user to list of users
                    print("verified")
                    delim = ","
                    sub_list.append(str(reduce(lambda x, y: str(x) + delim + str(y), user)))
                    sub_queue.pop(index)
                else:
                    if user[3] + expiration_time > time.time():
                        sub_queue.pop(index)
                index += 1
        await asyncio.sleep(1)


def verify_tx(user_wallet, expected_amount):
    tx_history = transactions_api.get_parsed_transaction_history(
        address="5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g")
    for tx in tx_history:
        if len(tx["nativeTransfers"]) > 0:
            for transfer in tx["nativeTransfers"]:
                if str(transfer["fromUserAccount"]) == user_wallet and str(
                        transfer["toUserAccount"]) == "DzoUHyo6jaEypWYyKSmhAiZmxcpjXuTNhXEyXmGWxHZ3":
                    if transfer[
                        "amount"] == expected_amount:  # here check also if he sends too much or too little in that case refund the user - transaction fee but needs to be at least 1$ to be refundable i think?
                        return True


def add_to_queue(user_tag, user_addy, subscription_type):
    print(user_tag)
    #                    0          1            2             3
    sub_queue.append([user_tag, user_addy, subscription_type, time.time()])


if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling(poll_interval=1)
    print("runnign....")
    loop = asyncio.get_event_loop()
    coros = [check_queue(), append_user_to_database()]
    loop.run_until_complete(asyncio.gather(*coros))
