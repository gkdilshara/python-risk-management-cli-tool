# ============================================================
#  models/account.py — Account CRUD
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from db.connection import DBConnection


class AccountModel:

    @staticmethod
    def all():
        cur = DBConnection.cursor()
        cur.execute("SELECT * FROM accounts ORDER BY id")
        return cur.fetchall()

    @staticmethod
    def get(account_id: int):
        cur = DBConnection.cursor()
        cur.execute("SELECT * FROM accounts WHERE id = %s", (account_id,))
        return cur.fetchone()

    @staticmethod
    def create(name: str, balance: float, currency: str = "USD"):
        cur = DBConnection.cursor()
        cur.execute(
            "INSERT INTO accounts (name, balance, currency) VALUES (%s, %s, %s)",
            (name, balance, currency),
        )
        return cur.lastrowid

    @staticmethod
    def update_balance(account_id: int, new_balance: float):
        cur = DBConnection.cursor()
        cur.execute(
            "UPDATE accounts SET balance = %s WHERE id = %s",
            (new_balance, account_id),
        )

    @staticmethod
    def delete(account_id: int):
        cur = DBConnection.cursor()
        cur.execute("DELETE FROM accounts WHERE id = %s", (account_id,))
