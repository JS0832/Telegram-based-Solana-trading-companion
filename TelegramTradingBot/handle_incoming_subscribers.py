from helius import TransactionsAPI
import asyncio
import telebot
import time
import dataBase

db = dataBase.DataBase()

transactions_api = TransactionsAPI("3e1717e1-bf69-45ae-af63-361e43b78961")
API_TOKEN = '7089696589:AAGA2jbfzBgmixtmf4X8I4ZRlZ5mdnAp5zk'
bot = telebot.TeleBot(API_TOKEN)


# handle refunds
# handle commission + cash back

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
                    bot.send_message(int(user[0]), "Transaction verified!\nYour "
                                                   "referral code is: " + str(user[5]) + "\nBot access: "
                                                                                         "https://t.me/SolAi9000bot")
                    print(str(user[0]) + " verified")
                    if str(user[6]) != "NONE":
                        pass
                    # credit_user_commission(str(user[1]), str(user[6]), str(user[2]))

        # here check for unknown transaction (ie any transfer from wallet that has nto been submitted via the bot)
        await asyncio.sleep(1)


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


'''
        def credit_user_commission(subscription_type, referral_code, user_address):  # finish later
            reward = 0  # amount to send to users in sol
            if str(subscription_type) == "1":  # monthly (0.4 sol)
                reward = 0.1
                cashback = 0.05
            elif str(subscription_type) == "2":  # 3-month (1 sol)
                reward = 0.3
                cashback = 0.15
            elif str(subscription_type) == "3":  # lifetime (3 sol)
                reward = 0.5
                cashback = 0.25
            referer = str(referral_code)[9:]  # fetches the telegram id of the other user
            with open('subscribers.txt', 'r', encoding='utf-8') as file:
                data = file.readlines()
                for index, user_item in enumerate(data):
                    if str(user_item.split()[0]) == referer:
                        if str(user_item.split()[5]) == "True":
                            print("sent reward of: " + str(reward))
                            comission_adress = user_item.split()[3]
                            cashback_adress = user_address
                            # pay cash back and comission
'''


def refund(target_wallet, amount):
    pass
    '''
        def check_for_invalid_tx():#checks if there is a tx that comes from unknown source
            current_time = int(time.time())
            expiration_interval = 600
            tx_history = transactions_api.get_parsed_transaction_history(
                address="5HUxqMarY94t1qQ5WV8yPgVmrjoMkXi9SzmWo2y2TU6g")
            for tx in tx_history:
                if current_time + expiration_interval > int(tx["timestamp"]) > current_time:
                    if len(tx["nativeTransfers"]) > 0:
                        for transfer in tx["nativeTransfers"]:
    '''


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


if __name__ == "__main__":
    print("runnign....")
    loop = asyncio.get_event_loop()
    coros = [check_users()]
    loop.run_until_complete(asyncio.gather(*coros))
