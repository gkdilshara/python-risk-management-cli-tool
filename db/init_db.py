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
    Ensure the target database, tables, and columns exist.
    Safe to run on every startup (uses CREATE ... IF NOT EXISTS and column checks).
    """

    db_name = DB_CONFIG["database"]

    # ── Step 1: connect WITHOUT specifying the database ──────
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
            id            INT AUTO_INCREMENT PRIMARY KEY,
            name          VARCHAR(100)   NOT NULL,
            account_type  ENUM('STANDARD', 'DERIV_OPTION') NOT NULL DEFAULT 'STANDARD',
            balance       DECIMAL(18,2)  NOT NULL DEFAULT 0.00,
            currency      VARCHAR(10)    NOT NULL DEFAULT 'USD',
            created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP
        )
        """,
        # trading_sessions
        """
        CREATE TABLE IF NOT EXISTS trading_sessions (
            id                      INT AUTO_INCREMENT PRIMARY KEY,
            account_id              INT          NOT NULL,
            session_name            VARCHAR(100) NOT NULL,
            trading_method          VARCHAR(50)  NOT NULL DEFAULT 'STANDARD',
            payout_percentage       DECIMAL(5, 2) DEFAULT NULL,
            reserved_stake_capital  DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
            target_profit           DECIMAL(18, 2) DEFAULT NULL,
            max_planned_trades      INT          DEFAULT NULL,
            status                  ENUM('ACTIVE', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'ACTIVE',
            created_at              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ended_at                DATETIME     DEFAULT NULL,
            notes                   TEXT         DEFAULT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
        """,
        # trades
        """
        CREATE TABLE IF NOT EXISTS trades (
            id                 INT AUTO_INCREMENT PRIMARY KEY,
            account_id         INT               NOT NULL,
            session_id         INT               DEFAULT NULL,
            symbol             VARCHAR(50)       NOT NULL,
            trade_type         ENUM('BUY','SELL','RISE','FALL') NOT NULL,
            quantity           DECIMAL(18,8)     NOT NULL,
            entry_price        DECIMAL(18,8)     NOT NULL,
            exit_price         DECIMAL(18,8)     DEFAULT NULL,
            stop_loss          DECIMAL(18,8)     DEFAULT NULL,
            take_profit        DECIMAL(18,8)     DEFAULT NULL,
            payout_percentage  DECIMAL(5, 2)      DEFAULT NULL,
            option_result      ENUM('WIN','LOSS') DEFAULT NULL,
            status             ENUM('OPEN','CLOSED','CANCELLED') NOT NULL DEFAULT 'OPEN',
            pnl                DECIMAL(18,2)     DEFAULT NULL,
            opened_at          DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
            closed_at          DATETIME          DEFAULT NULL,
            notes              TEXT              DEFAULT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES trading_sessions(id) ON DELETE SET NULL
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

    # ── Step 4: Run safe migrations for existing tables ──────
    _run_migrations(cur, db_name)

    conn.commit()
    cur.close()
    conn.close()

    # Pre-warm connection
    from db.connection import DBConnection
    DBConnection.get()


def _run_migrations(cur, db_name: str):
    """Dynamically add new columns to pre-existing tables if missing."""
    
    # 1. accounts.account_type
    cur.execute(
        """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'accounts' AND COLUMN_NAME = 'account_type'
        """,
        (db_name,),
    )
    if cur.fetchone()[0] == 0:
        cur.execute(
            "ALTER TABLE accounts ADD COLUMN account_type ENUM('STANDARD', 'DERIV_OPTION') NOT NULL DEFAULT 'STANDARD' AFTER name"
        )

    # 2. trading_sessions target_profit & max_planned_trades
    cur.execute(
        """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'trading_sessions' AND COLUMN_NAME = 'target_profit'
        """,
        (db_name,),
    )
    if cur.fetchone()[0] == 0:
        cur.execute(
            "ALTER TABLE trading_sessions ADD COLUMN target_profit DECIMAL(18, 2) DEFAULT NULL AFTER reserved_stake_capital"
        )

    cur.execute(
        """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'trading_sessions' AND COLUMN_NAME = 'max_planned_trades'
        """,
        (db_name,),
    )
    if cur.fetchone()[0] == 0:
        cur.execute(
            "ALTER TABLE trading_sessions ADD COLUMN max_planned_trades INT DEFAULT NULL AFTER target_profit"
        )

    # 3. trades columns: session_id, trade_type ENUM, payout_percentage, option_result
    cur.execute(
        """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'trades' AND COLUMN_NAME = 'session_id'
        """,
        (db_name,),
    )
    if cur.fetchone()[0] == 0:
        cur.execute(
            "ALTER TABLE trades ADD COLUMN session_id INT DEFAULT NULL AFTER account_id"
        )
        try:
            cur.execute(
                "ALTER TABLE trades ADD CONSTRAINT fk_trades_session FOREIGN KEY (session_id) REFERENCES trading_sessions(id) ON DELETE SET NULL"
            )
        except Error:
            pass

    cur.execute(
        """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'trades' AND COLUMN_NAME = 'payout_percentage'
        """,
        (db_name,),
    )
    if cur.fetchone()[0] == 0:
        cur.execute(
            "ALTER TABLE trades ADD COLUMN payout_percentage DECIMAL(5, 2) DEFAULT NULL AFTER take_profit"
        )

    cur.execute(
        """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'trades' AND COLUMN_NAME = 'option_result'
        """,
        (db_name,),
    )
    if cur.fetchone()[0] == 0:
        cur.execute(
            "ALTER TABLE trades ADD COLUMN option_result ENUM('WIN','LOSS') DEFAULT NULL AFTER payout_percentage"
        )

    # Expand trades.trade_type ENUM to include 'RISE' and 'FALL'
    try:
        cur.execute(
            "ALTER TABLE trades MODIFY COLUMN trade_type ENUM('BUY','SELL','RISE','FALL') NOT NULL"
        )
    except Error:
        pass
