# ============================================================
#  db/init_db.py — Auto-create database & tables on startup
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

import sys
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def init_database():
    """
    Ensure the target database and all tables exist.
    Called once at application startup — safe to run every time
    because every statement uses CREATE ... IF NOT EXISTS.
    """

    db_name = DB_CONFIG["database"]

    # ── Step 1: connect WITHOUT specifying the database ──────
    # (so we can create it if it doesn't exist yet)
    bootstrap_cfg = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    try:
        conn = mysql.connector.connect(**bootstrap_cfg)
    except Error as e:
        print(f"\n  [DB ERROR] Cannot connect to MySQL: {e}")
        print("  → Check your .env credentials and make sure MySQL is running.\n")
        sys.exit(1)

    cur = conn.cursor()

    # ── Step 2: create the database if missing ───────────────
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cur.execute(f"USE `{db_name}`")

    # ── Step 3: create tables ─────────────────────────────────
    statements = [
        # accounts
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(100)   NOT NULL,
            balance     DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
            currency    VARCHAR(10)    NOT NULL DEFAULT 'USD',
            created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP
        )
        """,
        # trades
        """
        CREATE TABLE IF NOT EXISTS trades (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            account_id   INT               NOT NULL,
            symbol       VARCHAR(20)       NOT NULL,
            trade_type   ENUM('BUY','SELL') NOT NULL,
            quantity     DECIMAL(18,8)     NOT NULL,
            entry_price  DECIMAL(18,8)     NOT NULL,
            exit_price   DECIMAL(18,8)     DEFAULT NULL,
            stop_loss    DECIMAL(18,8)     DEFAULT NULL,
            take_profit  DECIMAL(18,8)     DEFAULT NULL,
            status       ENUM('OPEN','CLOSED','CANCELLED') NOT NULL DEFAULT 'OPEN',
            pnl          DECIMAL(18,2)     DEFAULT NULL,
            opened_at    DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
            closed_at    DATETIME          DEFAULT NULL,
            notes        TEXT              DEFAULT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
        """,
        # risk_rules
        """
        CREATE TABLE IF NOT EXISTS risk_rules (
            id                  INT AUTO_INCREMENT PRIMARY KEY,
            account_id          INT           NOT NULL,
            max_risk_per_trade  DECIMAL(5,2)  NOT NULL DEFAULT 2.00,
            max_daily_loss      DECIMAL(5,2)  NOT NULL DEFAULT 5.00,
            max_open_trades     INT           NOT NULL DEFAULT 5,
            max_position_size   DECIMAL(5,2)  NOT NULL DEFAULT 10.00,
            created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
        """,
        # daily_journal
        """
        CREATE TABLE IF NOT EXISTS daily_journal (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            account_id   INT            NOT NULL,
            journal_date DATE           NOT NULL,
            total_trades INT            NOT NULL DEFAULT 0,
            winning      INT            NOT NULL DEFAULT 0,
            losing       INT            NOT NULL DEFAULT 0,
            gross_pnl    DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
            note         TEXT           DEFAULT NULL,
            created_at   DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_account_date (account_id, journal_date),
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
        """,
    ]

    for sql in statements:
        cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()

    # Re-connect properly (now the DB exists) via the shared singleton
    from db.connection import DBConnection
    DBConnection.get()  # pre-warms the connection
