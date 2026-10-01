# 📈 Trading Risk Management System CLI

> **A terminal-based risk management dashboard and position calculator for traders, powered by Python & MySQL.**  
> *Developed by Sasindu Dilshara*

---

## 🌟 Overview

**Trading Risk Management System CLI** is an interactive command-line interface application designed to help traders control risk, manage trading accounts, log daily performance, and enforce position sizing rules before executing trades.

Features zero-flicker arrow key navigation, MySQL database auto-initialization, real-time risk checks, and terminal styling.

---

## ✨ Features

- 🎯 **Interactive Arrow-Key Navigation**: Flicker-free terminal UI using ANSI cursor positioning.
- 🛢️ **MySQL Auto-Initialization**: Automatically creates database schemas and tables on startup via `.env` configuration.
- 🛡️ **Risk Rule Enforcement**: Set maximum risk per trade (%), daily loss limits, and maximum position size before opening positions.
- 📊 **Real-time Account Dashboard**: Overview of win rate, P&L, risk limits, and open trades.
- 📓 **Trading Journal**: Auto-calculated daily win/loss records with custom notes.
- 🧮 **Trading Calculators**: Built-in Position Size Calculator, Risk-to-Reward Ratio Calculator, and Pip Value Calculator.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **MySQL Server**

### 2. Installation
Clone the repository:
```bash
git clone https://github.com/<your-username>/risk-management-cli.git
cd risk-management-cli
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

*Note: The app automatically sets up all required MySQL tables on first run.*

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

## 👨‍💻 Author

**Sasindu Dilshara**
