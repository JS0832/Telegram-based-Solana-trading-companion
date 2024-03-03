import sqlite3
import tradingDataBase

trading_db = tradingDataBase.TradingDatabase()  # initialise


def generate_unique_referral_code(telegram_id):  # maybe make the code shorter tbh
    return "SolAiBot#" + str(telegram_id)


class DataBase:

    # creates a user database and sets a connection
    def __init__(self):
        self.connection = sqlite3.connect("bot_users.db",
                                          check_same_thread=False)  # check what the check next thread means
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute("""CREATE TABLE users(
                telegramId INTEGER,
                subscriptionType INTEGER,
                userWalletAddress TEXT,
                epoch INTEGER,
                subscriptionActivated TEXT,
                personalCode TEXT,
                providedReferralCode TEXT,
                cashbackRecieved INTEGER,
                totalComissionRecieved INTEGER,
                totalUsersRefered INTEGER
                )""")
            self.connection.commit()
        except sqlite3.Error:
            print("Database is Already created")

    def return_all_activated_users(self):
        sql = "SELECT * FROM users WHERE subscriptionActivated =?"
        self.cursor.execute(sql, ["True"])
        users = self.cursor.fetchall()
        return users

    # checking whether the user already exists
    def check_username_exists(self, telegram_id):
        sql = "SELECT * FROM users WHERE telegramId=?"
        self.cursor.execute(sql, [telegram_id])
        user = self.cursor.fetchone()
        if user is None:
            return False
        else:
            return True

    # check if a user has activated their subscription
    def check_user_activation(self, telegram_id):
        sql = "SELECT * FROM users WHERE telegramId=? AND subscriptionActivated == 'True'"
        self.cursor.execute(sql, [telegram_id])
        user = self.cursor.fetchone()
        if user is None:
            return False
        else:
            return True

    def check_unverified_users(self):
        sql = "SELECT * FROM users WHERE subscriptionActivated =?"
        self.cursor.execute(sql, ["False"])
        users = self.cursor.fetchall()
        if users is None:
            return False
        else:
            return users

    def check_subscription(self, telegram_id):
        sql = "SELECT * FROM users WHERE telegramId=? AND subscriptionActivated == 'True'"
        self.cursor.execute(sql, [telegram_id])
        user = self.cursor.fetchone()
        if user is None:
            return "none", "none"
        else:
            return user[2], user[4]

    # adding user
    def add_user(self, telegram_id, epoch, user_wallet_address, subscription_type, entered_code):
        personalCode = generate_unique_referral_code(telegram_id)  # add fucntion here to make this
        if not self.check_username_exists(telegram_id):
            sql = "INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?)"
            self.cursor.execute(sql,
                                (telegram_id, subscription_type, user_wallet_address, epoch, "False",
                                 personalCode, entered_code,
                                 0, 0, 0))
            self.connection.commit()
            trading_db.add_trading_user(telegram_id)  # adding to trading database
            return True
        else:
            return False

    # deleting user
    def delete_user(self, telegram_id):
        sql = "DELETE FROM users WHERE telegramId=?"
        self.cursor.execute(sql, [telegram_id])
        self.connection.commit()
        trading_db.update_active(telegram_id, "False")  # deactivates their trading ability(still keeps a record
        # incase they soon resubscribe)
        # possibly an (delete all my records option soon)

    # activating subscription (enable users default trading settings)
    def activate_user(self, telegram_id):
        sql = "UPDATE users SET subscriptionActivated = 'True' WHERE telegramId=?"
        self.cursor.execute(sql, [telegram_id])
        self.connection.commit()

    # def check_for_unauthorised_tx(self):
