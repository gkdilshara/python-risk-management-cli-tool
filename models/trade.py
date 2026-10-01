# ============================================================
#  models/trade.py — Trade CRUD + P&L
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from db.connection import DBConnection
from datetime import date


class TradeModel:

    @staticmethod
    def all(account_id: int, status: str = None, session_id: int = None):
        cur = DBConnection.cursor()
        query = "SELECT * FROM trades WHERE account_id = %s"
        params = [account_id]

        if session_id:
            query += " AND session_id = %s"
            params.append(session_id)

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY opened_at DESC"
        cur.execute(query, tuple(params))
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
        session_id: int = None,
        payout_percentage: float = None,
        option_result: str = None,
        notes: str = "",
    ):
        cur = DBConnection.cursor()
        cur.execute(
            """
            INSERT INTO trades
              (account_id, session_id, symbol, trade_type, quantity, entry_price,
               stop_loss, take_profit, payout_percentage, option_result, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                account_id,
                session_id,
                symbol.upper(),
                trade_type.upper(),
                quantity,
                entry_price,
                stop_loss,
                take_profit,
                payout_percentage,
                option_result.upper() if option_result else None,
                notes,
            ),
        )
        trade_id = cur.lastrowid

        # If option result is already known at creation (e.g. completed digital option trade)
        if option_result and trade_type.upper() in ("RISE", "FALL"):
            TradeModel.close_option(trade_id, option_result)

        return trade_id

    @staticmethod
    def close(trade_id: int, exit_price: float):
        """Close a standard trade, compute P&L and update account balance."""
        trade = TradeModel.get(trade_id)
        if not trade:
            return None, "Trade not found"
        if trade["status"] != "OPEN":
            return None, "Trade is not open"

        qty = float(trade["quantity"])
        ep  = float(trade["entry_price"])
        xp  = float(exit_price)

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

        # Update account balance
        cur.execute(
            "UPDATE accounts SET balance = balance + %s WHERE id = %s",
            (round(pnl, 2), trade["account_id"]),
        )
        return round(pnl, 2), None

    @staticmethod
    def close_option(trade_id: int, result: str):
        """Close a Deriv Option trade (WIN or LOSS) and calculate payout P&L."""
        trade = TradeModel.get(trade_id)
        if not trade:
            return None, "Trade not found"

        stake  = float(trade["quantity"])  # Quantity stores stake for options
        payout_pct = float(trade["payout_percentage"] or 95.0)

        res_upper = result.upper()
        if res_upper == "WIN":
            pnl = stake * (payout_pct / 100.0)
        else:
            pnl = -stake

        cur = DBConnection.cursor()
        cur.execute(
            """
            UPDATE trades
               SET status = 'CLOSED', option_result = %s, pnl = %s, closed_at = NOW()
             WHERE id = %s
            """,
            (res_upper, round(pnl, 2), trade_id),
        )

        # Update account balance
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
