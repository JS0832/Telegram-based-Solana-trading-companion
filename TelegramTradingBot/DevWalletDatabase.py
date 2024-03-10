# HERE STORE WALLETS OF THE DEV IN CASE SOEM REFRESHES MENAIGN T HEY MIHGT BE INTERESTED IN THE FUTURE TOO
import sqlite3


class DevWalletDataBase:
    def __init__(self):
        self.connection = sqlite3.connect("dev_wallets.db",
                                          check_same_thread=False)  # check what the check next thread means
        self.cursor3 = self.connection.cursor()
        try:  # will store the list as a coma separated list
            self.cursor3.execute("""CREATE TABLE users(
                tokenCa TEXT,
                DevWallets TEXT,
                )""")
            self.connection.commit()
        except sqlite3.Error:
            print("wallet Database is Already created")

    def check_token(self, token_ca):  # check if the token exists
        sql = "SELECT * FROM users WHERE tokenCa =?"
        self.cursor3.execute(sql, [token_ca])
        token = self.cursor3.fetchone()
        if token is None:
            return False
        else:
            return True

    def add_dev_wallets(self, token_ca, wallets):
        if not self.check_token(token_ca):
            sql = "INSERT INTO users VALUES (?,?)"
            self.cursor3.execute(sql,
                                 (token_ca, wallets))
            self.connection.commit()

    def return_dev_wallets(self, token_ca):
        sql = "SELECT * FROM users WHERE tokenCa =?"
        self.cursor3.execute(sql, [token_ca])
        token = self.cursor3.fetchone()
        return token[1]  # return the comma separated list of wallets
