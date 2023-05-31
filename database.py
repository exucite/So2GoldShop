import sqlite3

class Database:
    def __int__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

    def start(self):
        with self.connection:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (tg_id INT UNIQUE, referrer_id INT, gold INT, tg_username TEXT UNIQUE)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS gold_withdraw (tg_id INT, gold INT, tg_username TEXT, photo INT, id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, is_valid BOOL)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS payments (tg_id INT, tg_username TEXT, amount INT, payment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS questions (tg_id INT, text TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT, is_valid BOOL)""")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (exchange_rate REAL, minimum_of_replenishment INT, minimum_of_withdraw INT, id_of_compulsory_subscribe TEXT, procent_of_referrer INT)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS promocodes (promocodes TEXT, gold INT, activates TEXT, limit_users INTEGER)")


    def check_profile(self,user_id):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM users WHERE tg_id = ?""", (user_id,)).fetchall()

    def user_exists(self,user_id):
        with self.connection:
            if len(self.cursor.execute("""SELECT * FROM users WHERE tg_id = ?""", (user_id,)).fetchall()) == 0:
                return False
            else:
                return True

    def update_values(self,user_id,gold,username):
        with self.connection:
            return self.cursor.execute("""UPDATE users SET gold = ? WHERE tg_id = ? OR tg_username = ?""", (gold,user_id, username,))

    def add_user(self,user_id, gold, username, referrer_id):
        with self.connection:
            try:
                self.cursor.execute("""INSERT INTO users (tg_id, referrer_id, gold, tg_username) VALUES (?,?,?,?)""", (user_id, referrer_id, gold, username,))
            except sqlite3.IntegrityError:
                return False

    def check_all(self):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM users""").fetchall()

    def check_only_ids(self):
        with self.connection:
            return self.cursor.execute("""SELECT tg_id FROM users""").fetchall()

    def select_only_referrers(self,user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE referrer_id = ?", (user_id,)).fetchall()

    def add_gold_withdraw(self,user_id, amount_of_gold, username, photo):
        with self.connection:
            self.cursor.execute("""INSERT INTO gold_withdraw (tg_id, gold, tg_username, photo) VALUES (?,?,?,?)""", (user_id,amount_of_gold, username, photo))

    def check_all_withdraw(self):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM gold_withdraw""").fetchall()

    def check_withdraw_by_username(self,username):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM gold_withdraw WHERE tg_username = ?""", (username,)).fetchall()

    def delete_withdraw(self,username,user_id,id):
        with self.connection:
            self.cursor.execute("""DELETE FROM gold_withdraw WHERE tg_username = ? OR tg_id = ? OR id = ?""", (username,user_id,id,))

    def set_is_valid_withdraw_bool(self, bool, user_id, username):
        with self.connection:
            self.cursor.execute("""UPDATE gold_withdraw SET is_valid = ? WHERE tg_id = ? OR tg_username = ?""",(bool, user_id, username))

    def check_applications(self):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM gold_withdraw WHERE is_valid = 1""").fetchall()

    def select_only_tg_id(self,id):
        with self.connection:
            return self.cursor.execute("""SELECT tg_id FROM gold_withdraw WHERE id = ?""",(id,)).fetchall()

    def select_only_gold_withdraw(self,id):
        with self.connection:
            return self.cursor.execute("""SELECT gold FROM gold_withdraw WHERE id = ?""",(id,)).fetchall()

    def insert_into_payments(self,user_id,username,amount):
        with self.connection:
            return self.cursor.execute("""INSERT INTO payments (tg_id, tg_username, amount) VALUES (?,?,?)""", (user_id,username,amount))

    def select_from_payments(self,user_id,username,amount,payment_id):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM payments WHERE tg_id = ? OR tg_username = ? OR amount = ? OR payment_id = ?""", (user_id,username,amount,payment_id)).fetchall()

    def delete_payment(self,user_id,username,amount,payment_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM payments WHERE tg_id = ? OR tg_username = ? OR amount = ? OR payment_id = ?""", (user_id,username,amount,payment_id))

    def insert_into_questions(self,user_id,text):
        with self.connection:
            self.cursor.execute("""INSERT INTO questions (tg_id, text) VALUES (?,?)""",(user_id,text,))

    def select_from_questions(self,user_id,id):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM questions WHERE tg_id = ? OR id = ?""", (user_id,id,)).fetchall()

    def delete_from_questions(self,user_id,id):
        with self.connection:
            self.cursor.execute("""DELETE FROM questions WHERE tg_id = ? OR id = ?""", (user_id,id))

    def select_from_settings(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM settings").fetchall()
            if len(result) == 0:
                return False
            else:
                return result

    def insert_into_settings(self):
        with self.connection:
            if len(self.cursor.execute("SELECT * FROM settings").fetchall()) == 0:
                self.cursor.execute("INSERT INTO settings (exchange_rate, minimum_of_replenishment, minimum_of_withdraw, id_of_compulsory_subscribe, procent_of_referrer) VALUES (?,?,?,?,?)", (0.6,100,100,None,0,))
            else:
                pass

    def update_settings(self, exch_rate, minimum_of_replenishment, minimum_of_withdraw, compulsory_subscribe, procent_of_referrer):
        with self.connection:
            if exch_rate is not None:
                self.cursor.execute("UPDATE settings SET exchange_rate = ?", (exch_rate,))
            if minimum_of_replenishment is not None:
                self.cursor.execute("UPDATE settings SET minimum_of_replenishment = ?", (minimum_of_replenishment,))
            if minimum_of_withdraw is not None:
                self.cursor.execute("UPDATE settings SET minimum_of_withdraw = ?", (minimum_of_withdraw,))
            if compulsory_subscribe is not None:
                self.cursor.execute("UPDATE settings SET id_of_compulsory_subscribe = ?",(compulsory_subscribe,))
            if procent_of_referrer is not None:
                self.cursor.execute("UPDATE settings SET procent_of_referrer = ?",(procent_of_referrer,))

    def select_from_promos(self,as_array):
        with self.connection:
            promos = self.cursor.execute("SELECT * FROM promocodes").fetchall()
            if as_array:
                array_of_promos = []
                for i in promos[0]:
                    array_of_promos.append(i)
                return array_of_promos
            else:
                return promos

    def add_promo(self, promo, gold,limit):
        with self.connection:
            self.cursor.execute("INSERT INTO promocodes (promocodes, gold, limit_users) VALUES (?,?,?)",(promo,gold,limit,))

    def delete_promo(self,promo):
        with self.connection:
            self.cursor.execute("DELETE FROM promocodes WHERE promocodes = ?",(promo,))

    def delete_all_promos(self):
        with self.connection:
            self.cursor.execute("DELETE FROM promocodes")

    def select_by_promo(self, promo):
        with self.connection:
            return self.cursor.execute("SELECT * FROM promocodes WHERE promocodes = ?",(promo,)).fetchall()

    def insert_into_promo_activates(self,promo,user_id):
        with self.connection:
            self.cursor.execute("UPDATE promocodes SET activates = ? WHERE promocodes = ?",(user_id,promo,))

    def update_limit(self,limit, promo):
        with self.connection:
            self.cursor.execute("UPDATE promocodes SET limit_users = ? WHERE promocodes = ?",(limit,promo,))

    # def set_valid_question(self,id):
    #     with self.connection:
    #         self.cursor.execute("""UPDATE questions SET is_valid = 1 WHERE id = ?""",(id,))

    def check_questions(self):
        with self.connection:
            return self.cursor.execute("""SELECT * FROM questions""").fetchall()





# db = Database()
# db.connection = sqlite3.connect('database.db')
# db.cursor = db.connection.cursor()
# db.start()
# db.update_values(123)
# print(db.check_all())



