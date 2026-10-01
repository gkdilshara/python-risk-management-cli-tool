# ============================================================
#  models/journal.py — Daily Journal CRUD
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from db.connection import DBConnection
from datetime import date


class JournalModel:

    @staticmethod
    def all(account_id: int):
        cur = DBConnection.cursor()
        cur.execute(
            "SELECT * FROM daily_journal WHERE account_id = %s ORDER BY journal_date DESC",
            (account_id,),
        )
        return cur.fetchall()

    @staticmethod
    def get(account_id: int, for_date: date = None):
        if for_date is None:
            for_date = date.today()
        cur = DBConnection.cursor()
        cur.execute(
            "SELECT * FROM daily_journal WHERE account_id = %s AND journal_date = %s",
            (account_id, for_date),
        )
        return cur.fetchone()

    @staticmethod
    def upsert(account_id: int, for_date: date, note: str = ""):
        """Refresh the journal entry by re-counting trades for that day."""
        cur = DBConnection.cursor()
        cur.execute(
            """
            SELECT
              COUNT(*) AS total,
              SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS wins,
              SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) AS losses,
              COALESCE(SUM(pnl), 0) AS gross_pnl
            FROM trades
            WHERE account_id = %s AND status = 'CLOSED' AND DATE(closed_at) = %s
            """,
            (account_id, for_date),
        )
        stats = cur.fetchone()

        cur.execute(
            """
            INSERT INTO daily_journal
              (account_id, journal_date, total_trades, winning, losing, gross_pnl, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              total_trades = VALUES(total_trades),
              winning      = VALUES(winning),
              losing       = VALUES(losing),
              gross_pnl    = VALUES(gross_pnl),
              note         = IF(VALUES(note) != '', VALUES(note), note)
            """,
            (
                account_id, for_date,
                stats["total"] or 0,
                stats["wins"]  or 0,
                stats["losses"] or 0,
                stats["gross_pnl"] or 0,
                note,
            ),
        )
