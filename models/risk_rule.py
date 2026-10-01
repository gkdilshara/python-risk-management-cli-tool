# ============================================================
#  models/risk_rule.py — Risk Rules CRUD
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from db.connection import DBConnection


class RiskRuleModel:

    @staticmethod
    def get(account_id: int):
        cur = DBConnection.cursor()
        cur.execute(
            "SELECT * FROM risk_rules WHERE account_id = %s LIMIT 1",
            (account_id,),
        )
        return cur.fetchone()

    @staticmethod
    def create_defaults(account_id: int):
        cur = DBConnection.cursor()
        cur.execute(
            """
            INSERT IGNORE INTO risk_rules (account_id)
            VALUES (%s)
            """,
            (account_id,),
        )

    @staticmethod
    def update(account_id: int, max_risk: float, max_daily_loss: float,
               max_open: int, max_position: float):
        cur = DBConnection.cursor()
        existing = RiskRuleModel.get(account_id)
        if existing:
            cur.execute(
                """
                UPDATE risk_rules
                   SET max_risk_per_trade = %s,
                       max_daily_loss     = %s,
                       max_open_trades    = %s,
                       max_position_size  = %s
                 WHERE account_id = %s
                """,
                (max_risk, max_daily_loss, max_open, max_position, account_id),
            )
        else:
            cur.execute(
                """
                INSERT INTO risk_rules
                  (account_id, max_risk_per_trade, max_daily_loss,
                   max_open_trades, max_position_size)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (account_id, max_risk, max_daily_loss, max_open, max_position),
            )
