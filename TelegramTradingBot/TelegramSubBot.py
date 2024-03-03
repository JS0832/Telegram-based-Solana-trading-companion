# -*- coding: utf-8 -*-
import asyncio

from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot, types
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup

from solders.pubkey import Pubkey
from helius import TransactionsAPI
import time
from time import strftime, localtime

from TelegramTradingBot import dataBase

db = dataBase.DataBase()

API_TOKEN = '7089696589:AAGA2jbfzBgmixtmf4X8I4ZRlZ5mdnAp5zk'
bot = AsyncTeleBot(token=API_TOKEN, state_storage=StateMemoryStorage())
user_dict = {}  # temporary then it get moved to text file and subbed list
transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")
expiration = 600  # (600 seconds)


# Just create different states group
class MyStates(StatesGroup):
    proces_addy = State()
    process_referral = State()


# make it async together with the "handle incomming subscribers" (ie merge thoe into one)

@bot.message_handler(commands=['reset'])
async def reset(message):
    chat_id = message.chat.id
    if chat_id in user_dict:
        if user_dict[chat_id][1] + expiration < time.time():
            del user_dict[chat_id]
            await bot.send_message(chat_id,
                                   "time expired ,session was reset anyway.please try again now by using: /start")
        else:
            markup = types.InlineKeyboardMarkup(row_width=3)
            yes = types.InlineKeyboardButton("YES", callback_data="yes " + str(chat_id))
            no = types.InlineKeyboardButton("NO", callback_data="no " + str(chat_id))
            markup.add(yes, no)
            await bot.send_message(chat_id,
                                   "Are you sure you want to delete your previous submission? If you do you have to repeat "
                                   "the"
                                   "process again otherwise any payments will be refunded",
                                   reply_markup=markup)
    else:
        await bot.send_message(chat_id,
                               "Sorry but there doesnt seem to be any recent request for you,the request might of gotten "
                               "removed if 10 minutes have passed without any transaction.please use /start to begin the "
                               "process")


@bot.message_handler(commands=['referral'])
async def send_help(message):
    chat_id = message.chat.id
    referral = "AlphaPulse#" + str(chat_id)
    await bot.send_message(chat_id,
                           "Your Referral code is: " + referral)

    # reply ith referral code and also peopl who have been referred correctly
    # refenue of all referrals
    # individual comission history


@bot.message_handler(commands=['status'])
async def send_help(message):
    chat_id = message.chat.id
    check = db.check_subscription(chat_id)
    if check[0] == "none" and check[1] == "none":
        await bot.send_message(chat_id,
                               "you don't have an active subscription with us\nPlease use the /start command to begin")
    else:
        # calculate days left and subscription type
        if str(check[0]) == "1":
            end_epoch = int(check[1]) + (3600 * 24 * 30)
            end_date = str(strftime('%Y-%m-%d %H:%M:%S', localtime(end_epoch)))
            subtype = "Monthly"
            await bot.send_message(chat_id,
                                   f"you are one the {subtype} subscription\nEnd date: {end_date}")
        elif str(check[0]) == "2":
            end_epoch = int(check[1]) + (3600 * 24 * 90)
            end_date = str(strftime('%Y-%m-%d %H:%M:%S', localtime(end_epoch)))
            subtype = "3 Months"
            await bot.send_message(chat_id,
                                   f"you are one the {subtype} subscription\nEnd date: {end_date}")
        else:
            await bot.send_message(chat_id,
                                   "You have a Lifetime subscription.No future payments required to keep using our product")


@bot.message_handler(commands=['upgrade'])
async def send_help(message):
    await bot.reply_to(message,
                       "soon added.")


@bot.message_handler(commands=['help'])
async def send_help(message):
    await bot.reply_to(message,
                       "This is our custom subscription bot used to set up a subscription for our advanced Ai group.It is a "
                       "safe and easy way to make a payment.")


@bot.message_handler(commands=['debug'])  # remove this later
async def send_help(message):
    db.activate_user(5765234917)  # activate myself
    await bot.reply_to(message,
                       "admin made premium")


# Handle '/start'
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    allowed = False
    # whitelist the user the group
    chat_id = message.chat.id
    check = db.check_subscription(chat_id)
    if check[0] == "none" and check[1] == "none":
        if chat_id in user_dict:
            if not user_dict[chat_id][1] + expiration < time.time():
                await bot.send_message(chat_id,
                                       "seems like you tried to register for a subscription recently,if you made a mistake "
                                       "please"
                                       "come back in 10 minutes and repeat the process")
                return
            else:
                del user_dict[chat_id]
        allowed = True
    else:
        await bot.send_message(chat_id,
                               "You already have an active subscription with us\nYou can upgrade or view it's status by "
                               "using /upgrade or /status Commands")
    if allowed:
        user_dict[chat_id] = [chat_id, int(time.time()), "", ""]  # userid,epoch,wallet address,entered referral code
        markup = types.InlineKeyboardMarkup(row_width=2)
        has = types.InlineKeyboardButton("Yes", callback_data="ref_yes " + str(chat_id))
        not_has = types.InlineKeyboardButton("No", callback_data="ref_no " + str(chat_id))
        markup.add(has, not_has)
        await bot.send_message(chat_id, 'Did someone Refer you?', reply_markup=markup)


@bot.message_handler(state=MyStates.proces_addy)
async def process_addy(message):
    print("test")
    passed = True
    chat_id = message.chat.id
    user_address = message.text
    if chat_id in user_dict:
        if user_dict[chat_id][2] != "":
            if not user_dict[chat_id][1] + expiration < time.time():
                await bot.send_message(chat_id,
                                       "seems like you already provided a valid address,you can use /reset to start over or wait "
                                       " 10 minutes")
            else:
                await bot.send_message(chat_id,
                                       "10 minutes have passed...You can try subscribing again by using /start")
                del user_dict[chat_id]
                return  # to exit from further logic
        else:
            if len(str(user_address)) > 44 or len(str(user_address)) < 32 or str(
                    user_address) == "5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g":
                passed = False
            else:
                key = Pubkey.from_string(str(user_address))
                if key.is_on_curve():
                    user_dict[chat_id][2] = user_address
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    monthly = types.InlineKeyboardButton("One Month", callback_data="1 " + str(chat_id))
                    three_month = types.InlineKeyboardButton("3-Month", callback_data="2 " + str(chat_id))
                    lifetime = types.InlineKeyboardButton("Lifetime", callback_data="3 " + str(chat_id))
                    markup.add(monthly, three_month, lifetime)
                    await bot.send_message(chat_id,
                                           'Please select Subscription type:           \n\nOne Month: 0.4 $SOL\n3-Month: 1 $SOL\nLifetime: '
                                           '2 $SOL',
                                           reply_markup=markup)
                else:
                    passed = False
            if not passed:
                if user_address == "/restart":
                    await bot.send_message(chat_id,
                                           "you can now use /start to start over")
                    del user_dict[chat_id]
                    return
                else:
                    await bot.send_message(chat_id,
                                           "You have entered a invalid response above,please provide the wallet address that "
                                           "you will be sending funds from (do not send"
                                           "any private keys just the public address),use /restart to cancel")
                    await bot.set_state(message.from_user.id, MyStates.proces_addy, message.chat.id)
                    return


@bot.message_handler(state=MyStates.process_referral)
async def process_referral_code(message):
    print("test")
    passed = False
    chat_id = message.chat.id
    user_referral_code = message.text
    if chat_id in user_dict:
        if user_dict[chat_id][3] != "":
            if not user_dict[chat_id][1] + expiration < time.time():
                await bot.send_message(chat_id,
                                       "seems like you already provided a valid code,you can use /reset to start over or "
                                       "wait"
                                       " 10 minutes")
            else:
                await bot.send_message(chat_id,
                                       "10 minutes have passed...You can try subscribing again by using /start")
                del user_dict[chat_id]
                return  # to exit from further logic
        else:
            if len(user_referral_code) > 8:
                if (user_referral_code[0:9] == "SolAiBot#" and user_referral_code != "SolAiBot#" + str(chat_id) and
                        db.check_username_exists(user_referral_code[9:])):
                    user_dict[chat_id][3] = str(user_referral_code)
                    await bot.send_message(chat_id,
                                           "Thank you for the valid referral code,Now please provide the wallet address "
                                           "that you will be sending funds from (do not send"
                                           "any private keys just the public address)")
                    await bot.set_state(message.from_user.id, MyStates.proces_addy, message.chat.id)
                    return
            if not passed:
                if user_referral_code == "/restart":
                    await bot.send_message(chat_id,
                                           "you can now use /start to start over")
                    del user_dict[chat_id]
                    return
                else:
                    await bot.send_message(chat_id,
                                           "You have entered a invalid response above,please enter a valid code or use "
                                           "/restart to cancel")
                    await bot.set_state(message.from_user.id, MyStates.process_referral, message.chat.id)
                    return


@bot.callback_query_handler(func=lambda call: True)
async def confirm_and_process(callback):
    chat_id = int(callback.data.split(' ')[1])
    if chat_id in user_dict:
        if callback.data.split(' ')[0] == "ref_yes":
            if len(user_dict[chat_id][3]) == 0:
                await bot.send_message(chat_id,
                                       "Please enter a valid referral code")
                print(callback.message.from_user.id)
                await bot.set_state(chat_id, MyStates.process_referral, chat_id)
            return
        elif callback.data.split(' ')[0] == "ref_no":
            if len(user_dict[chat_id][3]) == 0:
                user_dict[chat_id][3] = "NULL"
                await bot.send_message(chat_id,
                                       "Ok No referral code will be required,please provide the wallet address that you"
                                       "will be sending funds from (do not send"
                                       "any private keys just the public address)")
                await bot.set_state(chat_id, MyStates.proces_addy, chat_id)
            return
        if callback.data.split(' ')[0] == "yes":

            del user_dict[chat_id]  # deletes the user from the dictionary
            if db.check_username_exists(chat_id):
                if not db.check_user_activation(chat_id):
                    db.delete_user(chat_id)
                    await bot.send_message(chat_id, "data deleted")
                else:
                    await bot.send_message(chat_id,
                                           "You cannot reset subscription after it has been paid.Please use /status "
                                           "to check more info regarding your subscription")
            else:
                await bot.send_message(chat_id, "you didn't apply for any subscription.you can start over using /start")
            return

        elif callback.data.split(' ')[0] == "no":
            await bot.send_message(chat_id,
                                   "ok I will not delete any data")

        if user_dict[chat_id][1] + expiration < time.time():
            await bot.send_message(chat_id,
                                   "10 minutes have passed...You can try subscribing again by using /start\nIf you already "
                                   "paid then you can check your subscription status using /status")
            del user_dict[chat_id]
        elif not user_dict[chat_id][1] + expiration < time.time() and db.check_username_exists(chat_id):
            await bot.send_message(chat_id,
                                   "Please come back in 10 minutes and use /start to try again or use /reset to start again "
                                   "sooner ")
        else:
            if db.check_user_activation(chat_id):
                await bot.send_message(chat_id,
                                       "You already have a subscription with us,please wait or use /upgrade to "
                                       "see your upgrade options")

                del user_dict[chat_id]
            else:
                db.add_user(chat_id, user_dict[chat_id][1], user_dict[chat_id][2], callback.data.split(' ')[0],
                            user_dict[chat_id][3])
                if callback.data.split(' ')[0] == "1":
                    option = "month"
                elif callback.data.split(' ')[0] == "2":
                    option = "3 months"
                else:
                    option = "Lifetime"
                await bot.send_message(chat_id,
                                       f'Thank you for providing your details \nYou have selected the *{option}* option\nSend funds to this wallet to unlock your '
                                       'subscription:\n\n`5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g`\n\nYou will receive a '
                                       'confirmation after the transaction has'
                                       'been completed\n\nExtra info: If you send too little or too much $SOL you will get a '
                                       'automatic refund minus transfer fees\nYou can upgrade your membership by using the command: '
                                       '/upgrade \nFor further enquiries please contact: memeDEV',
                                       parse_mode='MarkdownV2')


# async logic for handing user submissions

async def check_users():  # Here I can
    expiration_time = 600
    while True:
        user_list = db.check_unverified_users()
        for user in user_list:
            if int(user[3]) + expiration_time < time.time():
                db.delete_user(user[0])
            else:
                expected_sol = 0
                users_subscription = str(user[1])
                if users_subscription == "1":  # monthly (0.4 sol)
                    expected_sol = 0.4
                elif users_subscription == "2":  # 3-month (1 sol)
                    expected_sol = 1.0
                elif users_subscription == "3":  # lifetime (3 sol)
                    expected_sol = 2.0
                if verify_tx(str(user[2]), expected_sol, int(user[3])):  # passed
                    db.activate_user(user[0])
                    await bot.send_message(int(user[0]), "Transaction verified!\nYour "
                                                         "referral code is: " + str(user[5]) + "\nBot access: "
                                                                                               "https://t.me/AlphaPulseBot")
                    print(str(user[0]) + " verified")
                    if str(user[6]) != "NONE":
                        pass
                    # credit_user_commission(str(user[1]), str(user[6]), str(user[2]))

        # here check for unknown transaction (ie any transfer from wallet that has nto been submitted via the bot)
        await asyncio.sleep(1)


def verify_tx(user_wallet, expected_amount, epoch):
    expiration_interval = 600
    tx_history = transactions_api.get_parsed_transaction_history(
        address="5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g")
    for tx in tx_history:
        if epoch + expiration_interval > int(tx["timestamp"]) > epoch:
            if len(tx["nativeTransfers"]) > 0:
                for transfer in tx["nativeTransfers"]:
                    if str(transfer["fromUserAccount"]) == user_wallet and str(
                            transfer["toUserAccount"]) == "5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g":
                        if float(int(transfer["amount"])) / float(10 ** 9) == expected_amount:
                            return True


def check_expiration(subscription_type, users_subscription_time):
    duration = 0
    if subscription_type == "1":  # monthly (0.4 sol)
        duration = 60 * 60 * 24 * 30
    elif subscription_type == "2":  # 3-month (1 sol)
        duration = 60 * 60 * 24 * 90
    elif subscription_type == "3":  # lifetime (3 sol)
        return False
    if users_subscription_time + duration < int(time.time()):
        return True


async def remove_expired_user():
    users = db.return_all_activated_users()
    for user in users:
        if check_expiration(str(user[1]), int(user[3])):
            db.delete_user(user[0])


if __name__ == "__main__":
    print("runnign....")
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    loop = asyncio.get_event_loop()
    coros = [check_users(), bot.polling()]
    loop.run_until_complete(asyncio.gather(*coros))
