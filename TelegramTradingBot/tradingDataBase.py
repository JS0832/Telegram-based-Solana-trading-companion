# here we will store user private keys
# open positions
# user auto buy/sell settings
# store their grinder wallet
# ect...
import sqlite3
import create_users_public_private_key


class TradingDatabase:
    def __init__(self):
        self.connection = sqlite3.connect("trading_database.db",
                                          check_same_thread=False)  # check what the check next thread means
        self.cursor2 = self.connection.cursor()
        try:
            self.cursor2.execute("""CREATE TABLE tradingusers(
                telegramId INTEGER,
                TradingWalletAddress TEXT,
                CurrentPrivateKey TEXT,
                SolAmountForAutoBuy TEXT,
                AutoBuy TEXT,
                SellWithDev TEXT,
                AutoSell TEXT,
                AutoSellSettings TEXT,
                SentimentPings INTEGER,
                Active TEXT,
                PingSettings TEXT,
                openPosition TEXT,
                slippage TEXT
                )""")
            self.connection.commit()
        except sqlite3.Error:
            print("TradingDatabase is Already created")

    def check_user_exist(self, telegram_id):
        sql = "SELECT * FROM tradingusers WHERE telegramId =?"
        self.cursor2.execute(sql, [telegram_id])
        user = self.cursor2.fetchone()  # should be only one ofc
        if user is None:
            return False
        else:
            return True

    def add_trading_user(self, telegram_id):  # INITIALISE NEW USER
        sql = "INSERT INTO tradingusers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
        public_address, private_key = create_users_public_private_key.create_trading_wallet()
        self.cursor2.execute(sql,
                             (telegram_id, public_address, private_key, "1", "OFF", "OFF", "OFF", "NULL", 3, "False",
                              "DEFAULT", "NULL", "1"))
        # IF PING SETTINGS ARE CHANGED BY USER IT WILL BE A COMMA SEPARATED LIST OF VALUES
        self.connection.commit()

    def return_all_settings(self, telegram_id):
        sql = "SELECT * FROM tradingusers WHERE telegramId =?"
        self.cursor2.execute(sql, [telegram_id])
        user_settings = self.cursor2.fetchone()  # should be only one ofc
        return user_settings

    # Funds Management
    def create_new_wallet(self, telegram_id):
        temp = create_users_public_private_key.create_trading_wallet()
        sql = "UPDATE tradingusers SET TradingWalletAddress =? , CurrentPrivateKey =? WHERE telegramId=?"
        self.cursor2.execute(sql, [temp[0], temp[1], telegram_id])
        self.connection.commit()

    # sore a floating point in text format
    def update_sol_amount_buy(self, telegram_id, sol_amount):  # ITS TEXT BECAUSE WE WANT TO STORE AS FLOAT
        sql = "UPDATE tradingusers SET SolAmountForAutoBuy =? WHERE telegramId=?"
        self.cursor2.execute(sql, [sol_amount, telegram_id])
        self.connection.commit()

    def update_slippage(self, telegram_id, slippage):
        sql = "UPDATE tradingusers SET slippage =? WHERE telegramId=?"
        self.cursor2.execute(sql, [slippage, telegram_id])
        self.connection.commit()

    def update_auto_buy(self, telegram_id, auto_buy):  # ITS TEXT BECAUSE WE WANT TO STORE AF FLOAT
        sql = "UPDATE tradingusers SET AutoBuy =? WHERE telegramId=?"
        self.cursor2.execute(sql, [auto_buy, telegram_id])
        self.connection.commit()

    def update_sell_with_dev(self, telegram_id, sell_with_dev):  # ITS TEXT BECAUSE WE WANT TO STORE AF FLOAT
        sql = "UPDATE tradingusers SET SellWithDev =? WHERE telegramId=?"
        self.cursor2.execute(sql, [sell_with_dev, telegram_id])
        self.connection.commit()

    def update_auto_sell(self, telegram_id, auto_sell):  # ITS TEXT BECAUSE WE WANT TO STORE AF FLOAT
        sql = "UPDATE tradingusers SET AutoSell =? WHERE telegramId=?"
        self.cursor2.execute(sql, [auto_sell, telegram_id])
        self.connection.commit()

    def update_auto_sell_settings(self, telegram_id, auto_sell_settings):  # ITS TEXT BECAUSE WE WANT TO STORE AF FLOAT
        sql = "UPDATE tradingusers SET AutoSellSettings =? WHERE telegramId=?"
        self.cursor2.execute(sql, [auto_sell_settings, telegram_id])
        self.connection.commit()

    def update_sentiment_pings(self, telegram_id, update_sentiment_pings):  # ITS TEXT BECAUSE WE WANT TO STORE AF FLOAT
        sql = "UPDATE tradingusers SET SentimentPings =? WHERE telegramId=?"
        self.cursor2.execute(sql, [update_sentiment_pings, telegram_id])
        self.connection.commit()

    def reset_user(self, telegram_id):  # ITS TEXT BECAUSE WE WANT TO STORE AF FLOAT
        sql = ("UPDATE tradingusers SET SolAmountForAutoBuy=? AutoBuy=? SellWithDev=? AutoSell=? AutoSellSettings=? "
               "SentimentPings=? ping_settings=? WHERE telegramId=?")
        self.cursor2.execute(sql, ["1", "OFF", "OFF", "OFF", "NULL", 3, telegram_id, "DEFAULT"])
        self.connection.commit()

    def update_active(self, telegram_id, active):  # ITS TEXT BECAUSE WE WANT TO STORE AF FLOAT
        sql = "UPDATE tradingusers SET Active =? WHERE telegramId=?"
        self.cursor2.execute(sql, [active, telegram_id])
        self.connection.commit()

    # PING SETTINGS LAYOUT(MINIMUM INITIAL LIQUIDITY,MINIMUM LIQUIDTY BURNED,TOKENS SENT TO LP,RISK LEVEL)
    def update_ping_settings(self, telegram_id, ping_settings):
        sql = "UPDATE tradingusers SET PingSettings =? WHERE telegramId=?"
        self.cursor2.execute(sql, [ping_settings, telegram_id])
        self.connection.commit()
        # I think I might just store it as comma separated values

    def reset_ping_settings(self, telegram_id):
        sql = "UPDATE tradingusers SET PingSettings =? WHERE telegramId=?"
        self.cursor2.execute(sql, ["DEFAULT", telegram_id])
        self.connection.commit()

    # trading a token
    def check_sol_order_size(self, telegram_id):  # check how much sol to spend per buy order (it's adjusted by the user
        # in the settings to his own preference)
        sql = "SELECT * FROM users WHERE telegramId=?"
        self.cursor2.execute(sql, [telegram_id])
        user = self.cursor2.fetchone()
        return user[3]  # returns a string so need to convert it to a float

    def open_a_position(self, telegram_id, token_ca, sol_used, amount_of_tokens_received):
        temp_list = [telegram_id, token_ca, sol_used, amount_of_tokens_received]
        position_string = ",".join(temp_list)
        sql = "UPDATE tradingusers SET openPosition=? WHERE telegramId=?"
        self.cursor2.execute(sql, [position_string, telegram_id])
        self.connection.commit()
