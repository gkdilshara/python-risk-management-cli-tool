# ============================================================
#  models/trade.py — Trade CRUD + P&L
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from db.connection import DBConnection
from datetime import date


class TradeModel:

    @staticmethod
    def all(account_id: int, status: str = None):
        cur = DBConnection.cursor()
        if status:
            cur.execute(
                "SELECT * FROM trades WHERE account_id = %s AND status = %s ORDER BY opened_at DESC",
                (account_id, status),
            )
        else:
            cur.execute(
                "SELECT * FROM trades WHERE account_id = %s ORDER BY opened_at DESC",
                (account_id,),
            )
        return cur.fetchall()

    @staticmethod
    def get(trade_id: int):
        cur = DBConnection.cursor()
        cur.execute("SELECT * FROM trades WHERE id = %s", (trade_id,))
        return cur.fetchone()

    @staticmethod
    def open_trades_count(account_id: int):
        cur = DBConnection.cursor()
        cur.execute(
            "SELECT COUNT(*) as cnt FROM trades WHERE account_id = %s AND status = 'OPEN'",
            (account_id,),
        )
        row = cur.fetchone()
        return row["cnt"] if row else 0

    @staticmethod
    def create(
        account_id: int,
        symbol: str,
        trade_type: str,
        quantity: float,
        entry_price: float,
        stop_loss: float = None,
        take_profit: float = None,
        notes: str = "",
    ):
        cur = DBConnection.cursor()
        cur.execute(
            """
            INSERT INTO trades
              (account_id, symbol, trade_type, quantity, entry_price, stop_loss, take_profit, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (account_id, symbol.upper(), trade_type.upper(), quantity,
             entry_price, stop_loss, take_profit, notes),
        )
        return cur.lastrowid

    @staticmethod
    def close(trade_id: int, exit_price: float):
        """Close a trade, compute P&L and update account balance."""
        trade = TradeModel.get(trade_id)
        if not trade:
            return None, "Trade not found"
        if trade["status"] != "OPEN":
            return None, "Trade is not open"

        qty  = float(trade["quantity"])
        ep   = float(trade["entry_price"])
        xp   = float(exit_price)

        if trade["trade_type"] == "BUY":
            pnl = (xp - ep) * qty
        else:
            pnl = (ep - xp) * qty

        cur = DBConnection.cursor()
        cur.execute(
            """
            UPDATE trades
               SET status = 'CLOSED', exit_price = %s, pnl = %s, closed_at = NOW()
             WHERE id = %s
            """,
            (xp, round(pnl, 2), trade_id),
        )

        # update account balance
        cur.execute(
            "UPDATE accounts SET balance = balance + %s WHERE id = %s",
            (round(pnl, 2), trade["account_id"]),
        )
        return round(pnl, 2), None

    @staticmethod
    def cancel(trade_id: int):
        cur = DBConnection.cursor()
        cur.execute(
            "UPDATE trades SET status = 'CANCELLED' WHERE id = %s AND status = 'OPEN'",
            (trade_id,),
        )

    @staticmethod
    def daily_pnl(account_id: int, for_date: date = None):
        if for_date is None:
            for_date = date.today()
        cur = DBConnection.cursor()
        cur.execute(
            """
            SELECT COALESCE(SUM(pnl), 0) AS total
              FROM trades
             WHERE account_id = %s
               AND status = 'CLOSED'
               AND DATE(closed_at) = %s
            """,
            (account_id, for_date),
        )
        row = cur.fetchone()
        return float(row["total"]) if row else 0.0
