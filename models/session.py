# ============================================================
#  models/session.py — Trading Session CRUD & Stats
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from db.connection import DBConnection


class SessionModel:

    @staticmethod
    def create(
        account_id: int,
        session_name: str,
        trading_method: str = "STANDARD",
        payout_percentage: float = None,
        reserved_stake_capital: float = 0.0,
        notes: str = "",
    ) -> int:
        cur = DBConnection.cursor()
        cur.execute(
            """
            INSERT INTO trading_sessions
              (account_id, session_name, trading_method, payout_percentage, reserved_stake_capital, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                account_id,
                session_name,
                trading_method.upper(),
                payout_percentage,
                reserved_stake_capital,
                notes,
            ),
        )
        return cur.lastrowid

    @staticmethod
    def all(account_id: int = None, status: str = None):
        cur = DBConnection.cursor()
        query = """
            SELECT s.*, a.name AS account_name, a.account_type, a.currency
              FROM trading_sessions s
              JOIN accounts a ON s.account_id = a.id
        """
        params = []
        conditions = []

        if account_id:
            conditions.append("s.account_id = %s")
            params.append(account_id)
        if status:
            conditions.append("s.status = %s")
            params.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY s.created_at DESC"
        cur.execute(query, tuple(params))
        return cur.fetchall()

    @staticmethod
    def get(session_id: int):
        cur = DBConnection.cursor()
        cur.execute(
            """
            SELECT s.*, a.name AS account_name, a.account_type, a.currency
              FROM trading_sessions s
              JOIN accounts a ON s.account_id = a.id
             WHERE s.id = %s
            """,
            (session_id,),
        )
        return cur.fetchone()

    @staticmethod
    def get_active(account_id: int):
        cur = DBConnection.cursor()
        cur.execute(
            """
            SELECT * FROM trading_sessions
             WHERE account_id = %s AND status = 'ACTIVE'
             ORDER BY created_at DESC
            """,
            (account_id,),
        )
        return cur.fetchall()

    @staticmethod
    def complete(session_id: int, notes: str = ""):
        cur = DBConnection.cursor()
        if notes:
            cur.execute(
                """
                UPDATE trading_sessions
                   SET status = 'COMPLETED', ended_at = NOW(), notes = CONCAT(COALESCE(notes, ''), '\n', %s)
                 WHERE id = %s
                """,
                (notes, session_id),
            )
        else:
            cur.execute(
                """
                UPDATE trading_sessions
                   SET status = 'COMPLETED', ended_at = NOW()
                 WHERE id = %s
                """,
                (session_id,),
            )

    @staticmethod
    def cancel(session_id: int):
        cur = DBConnection.cursor()
        cur.execute(
            """
            UPDATE trading_sessions
               SET status = 'CANCELLED', ended_at = NOW()
             WHERE id = %s
            """,
            (session_id,),
        )

    @staticmethod
    def get_stats(session_id: int):
        """Calculate live statistics for trades belonging to a session."""
        session = SessionModel.get(session_id)
        if not session:
            return None

        cur = DBConnection.cursor()
        cur.execute(
            """
            SELECT
              COUNT(*) AS total_trades,
              SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS wins,
              SUM(CASE WHEN pnl <= 0 AND pnl IS NOT NULL THEN 1 ELSE 0 END) AS losses,
              COALESCE(SUM(pnl), 0) AS total_pnl,
              COALESCE(SUM(quantity), 0) AS total_staked
            FROM trades
            WHERE session_id = %s
            """,
            (session_id,),
        )
        row = cur.fetchone()

        total_trades = row["total_trades"] or 0
        wins         = row["wins"] or 0
        losses       = row["losses"] or 0
        total_pnl    = float(row["total_pnl"] or 0.0)
        total_staked = float(row["total_staked"] or 0.0)

        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
        reserved_cap = float(session["reserved_stake_capital"])
        remaining_cap = reserved_cap + total_pnl

        return {
            "session": session,
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "total_staked": total_staked,
            "reserved_capital": reserved_cap,
            "remaining_capital": remaining_cap,
        }
