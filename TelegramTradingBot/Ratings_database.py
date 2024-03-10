import sqlite3


class TokenRateDataBase:
    def __init__(self):
        self.connection = sqlite3.connect("tokenratings.db",
                                          check_same_thread=False)  # check what the check next thread means
        self.cursor3 = self.connection.cursor()
        try:  # will store the list as a coma separated list
            self.cursor3.execute("""CREATE TABLE tokenrate(
                tokenCa TEXT,
                Ratings TEXT,
                UsersWhoRated TEXT
                )""")
            self.connection.commit()
        except sqlite3.Error:
            print("ratings Database is Already created")

    def check_token(self, token_ca):  # check if the token exists
        sql = "SELECT * FROM tokenrate WHERE tokenCa =?"
        self.cursor3.execute(sql, [token_ca])
        token = self.cursor3.fetchone()
        if token is None:
            return False
        else:
            return True

    def fetch_token_data(self, token_ca):  # check if the token exists
        sql = "SELECT * FROM tokenrate WHERE tokenCa =?"
        self.cursor3.execute(sql, [token_ca])
        token = self.cursor3.fetchone()
        return token

    def add_token(self, token_ca):
        if not self.check_token(token_ca):
            sql = "INSERT INTO tokenrate VALUES (?,?,?)"
            self.cursor3.execute(sql,
                                 (token_ca, "d,d", "d,d"))  # dummy value to prevent bug
            self.connection.commit()

    def check_if_user_rated(self, token_ca):
        sql = "SELECT * FROM tokenrate WHERE tokenCa =?"
        self.cursor3.execute(sql, [token_ca])
        token = self.cursor3.fetchone()
        return token[1]  # return the comma separated list of wallets

    def add_rating(self, token_ca, user_id, rating_value):
        sql = "UPDATE tokenrate SET Ratings=? UsersWhoRated=?  WHERE tokenCa=?"
        temp_users_who_rated = self.fetch_token_data(token_ca)[1].split(",")  # list of users who rated the token
        temp_users_who_rated.append(user_id)
        users_string = ",".join(temp_users_who_rated)
        # now list of ratings:
        temp_rating_list = self.fetch_token_data(token_ca)[2].split(",")  # list of users who rated the token
        temp_rating_list.append(rating_value)
        rating_string = ",".join(temp_rating_list)
        self.cursor3.execute(sql, [rating_string, users_string, str(token_ca)])
        self.connection.commit()

        # add the info back to db
