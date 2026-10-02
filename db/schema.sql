-- ============================================================
--  Risk Management System — MySQL Schema
--  by Sasindu Dilshara
-- ============================================================

CREATE DATABASE IF NOT EXISTS risk_management
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE risk_management;

-- ── Accounts ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS accounts (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    account_type  ENUM('STANDARD', 'DERIV_OPTION') NOT NULL DEFAULT 'STANDARD',
    balance       DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    currency      VARCHAR(10)  NOT NULL DEFAULT 'USD',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ── Trading Sessions ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trading_sessions (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    account_id              INT          NOT NULL,
    session_name            VARCHAR(100) NOT NULL,
    trading_method          VARCHAR(50)  NOT NULL DEFAULT 'STANDARD', -- e.g. 'STANDARD', 'RISE_FALL'
    payout_percentage       DECIMAL(5, 2) DEFAULT NULL,            -- e.g. 95.00 for Deriv Option
    reserved_stake_capital  DECIMAL(18, 2) NOT NULL DEFAULT 0.00,  -- Reserved capital allocated
    target_profit           DECIMAL(18, 2) DEFAULT NULL,           -- Target profit goal for the session
    max_planned_trades      INT          DEFAULT NULL,             -- Amount of willing/planned trades
    status                  ENUM('ACTIVE', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'ACTIVE',
    created_at              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at                DATETIME     DEFAULT NULL,
    notes                   TEXT         DEFAULT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- ── Trades ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trades (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    account_id         INT          NOT NULL,
    session_id         INT          DEFAULT NULL,
    symbol             VARCHAR(50)  NOT NULL,
    trade_type         ENUM('BUY','SELL','RISE','FALL') NOT NULL,
    quantity           DECIMAL(18, 8) NOT NULL,                    -- Qty or Stake Amount
    entry_price        DECIMAL(18, 8) NOT NULL,                    -- Entry price or Stake Amount
    exit_price         DECIMAL(18, 8) DEFAULT NULL,
    stop_loss          DECIMAL(18, 8) DEFAULT NULL,
    take_profit        DECIMAL(18, 8) DEFAULT NULL,
    payout_percentage  DECIMAL(5, 2)  DEFAULT NULL,                -- For option trades
    option_result      ENUM('WIN','LOSS') DEFAULT NULL,            -- For option trades
    status             ENUM('OPEN','CLOSED','CANCELLED') NOT NULL DEFAULT 'OPEN',
    pnl                DECIMAL(18, 2) DEFAULT NULL,
    opened_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at          DATETIME     DEFAULT NULL,
    notes              TEXT         DEFAULT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES trading_sessions(id) ON DELETE SET NULL
);

-- ── Risk Rules ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS risk_rules (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    account_id           INT          NOT NULL,
    max_risk_per_trade   DECIMAL(5, 2) NOT NULL DEFAULT 2.00,   -- % of balance
    max_daily_loss       DECIMAL(5, 2) NOT NULL DEFAULT 5.00,   -- % of balance
    max_open_trades      INT          NOT NULL DEFAULT 5,
    max_position_size    DECIMAL(5, 2) NOT NULL DEFAULT 10.00,  -- % of balance
    created_at           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- ── Daily Journal ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_journal (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    account_id   INT          NOT NULL,
    journal_date DATE         NOT NULL,
    total_trades INT          NOT NULL DEFAULT 0,
    winning      INT          NOT NULL DEFAULT 0,
    losing       INT          NOT NULL DEFAULT 0,
    gross_pnl    DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    note         TEXT         DEFAULT NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_account_date (account_id, journal_date),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
