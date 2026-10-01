# 📈 Trading Risk Management System CLI

> **A terminal-based risk management dashboard, trading session tracker, and position calculator for traders, powered by Python & MySQL.**  
> *Developed by Sasindu Dilshara*

---

## 🌟 Overview

**Trading Risk Management System CLI** is an interactive command-line application designed to help traders manage risk, track trading sessions, log daily performance, and execute trades across multiple account types—including **Standard Trading Accounts** and **Deriv Option Trading Accounts** (Rise/Fall options).

Features zero-flicker ANSI arrow key navigation, automatic MySQL schema migrations, session confirmation workflows, and real-time P&L / payout calculations.

---

## ✨ Key Features

- 🎯 **Interactive Arrow-Key Navigation**: Flicker-free terminal UI using ANSI cursor positioning.
- 👥 **Multiple Account Types**:
  - **Standard Trading Account**: Forex, Stocks, Crypto (`BUY`/`SELL` positions with Stop-Loss & Take-Profit).
  - **Deriv Option Trading Account**: Digital/Binary Options with **Rise / Fall** (`RISE`/`FALL`) trading methods.
- ⏱️ **Trading Sessions Management**:
  - Auto-fetched session timestamps.
  - Option trading parameters: **Trading Method** (Rise/Fall), **Payout %** (e.g. `95.0%`), and **Reserved Stake Capital**.
  - **Interactive Confirmation Dialog**: Explicit confirmation prompt before saving a session.
  - Live session statistics (Win Rate, Total Staked, Session P&L, Remaining Reserved Capital).
- 🛢️ **MySQL Auto-Initialization & Dynamic Migrations**: Automatically creates database schemas and safely migrates existing tables on startup via `.env`.
- 🛡️ **Risk Rule Enforcement**: Set maximum risk per trade (%), daily loss limits, and maximum position size before opening positions.
- 📊 **Real-time Account Dashboard**: Overview of account types, active trading sessions, win rate, P&L, risk limits, and open trades.
- 📓 **Trading Journal**: Auto-calculated daily win/loss records with custom notes.
- 🧮 **Risk Calculators**: Position Size Calculator, Risk-to-Reward Ratio Calculator, and Pip Value Calculator.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **MySQL Server**

### 2. Installation
Clone the repository:
```bash
git clone https://github.com/gkdilshara/python-risk-management-cli-tool.git
cd python-risk-management-cli-tool
```

Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Setup
Copy `.env.example` to `.env` and fill in your MySQL credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=risk_management
DB_CHARSET=utf8mb4
```

### 4. Running the Application
**Windows:**
Double-click `run.bat` or execute in PowerShell:
```cmd
.\run.bat
```

**Linux / macOS:**
```bash
python main.py
```

*Note: The application automatically initializes and migrates MySQL database tables on startup.*

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 👨‍💻 Author

**Sasindu Dilshara**  
GitHub: [@gkdilshara](https://github.com/gkdilshara)
