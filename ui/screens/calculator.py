# ============================================================
#  ui/screens/calculator.py — Position Size & Risk Calculator
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from ui.helpers import *
from ui.theme   import *


def screen_calculator():
    while True:
        choice = arrow_menu(
            "RISK CALCULATOR",
            [
                "📐  Position Size Calculator",
                "💰  R:R Ratio Calculator",
                "📊  Pip Value Calculator",
                "🔙  Back to Main Menu",
            ],
        )

        if choice == 0:   _position_size()
        elif choice == 1: _rr_ratio()
        elif choice == 2: _pip_value()
        elif choice in (3, -1): break


def _position_size():
    clear()
    print_logo()
    section_header("POSITION SIZE CALCULATOR")
    print(f"  {C_DIM}Calculate optimal position size based on your risk tolerance.{C_RESET}\n")

    balance    = prompt_float("Account balance")
    risk_pct   = prompt_float("Risk per trade (%)", 2.0)
    entry      = prompt_float("Entry price")
    stop_loss  = prompt_float("Stop loss price")

    if entry == stop_loss:
        error("Entry and stop loss cannot be the same.")
        pause()
        return

    risk_amount = balance * (risk_pct / 100)
    sl_distance = abs(entry - stop_loss)
    position    = risk_amount / sl_distance
    pos_value   = position * entry

    print()
    print(C_BORDER + "  ┌──────────────────────────────────────────┐")
    print(C_BORDER + "  │           CALCULATION RESULTS             │")
    print(C_BORDER + "  ├──────────────────────────────────────────┤")
    _result_line("Risk Amount",     f"{risk_amount:,.2f}")
    _result_line("Stop Distance",   f"{sl_distance:.6f}")
    _result_line("Position Size",   f"{position:.4f} units")
    _result_line("Position Value",  f"{pos_value:,.2f}")
    print(C_BORDER + "  └──────────────────────────────────────────┘")
    pause()


def _rr_ratio():
    clear()
    print_logo()
    section_header("RISK : REWARD RATIO CALCULATOR")
    print(f"  {C_DIM}Analyse potential profit vs risk on a trade.{C_RESET}\n")

    entry      = prompt_float("Entry price")
    stop_loss  = prompt_float("Stop loss price")
    take_profit = prompt_float("Take profit price")

    risk   = abs(entry - stop_loss)
    reward = abs(take_profit - entry)

    if risk == 0:
        error("Risk cannot be zero.")
        pause()
        return

    rr = reward / risk

    print()
    print(C_BORDER + "  ┌──────────────────────────────────────────┐")
    print(C_BORDER + "  │           CALCULATION RESULTS             │")
    print(C_BORDER + "  ├──────────────────────────────────────────┤")
    _result_line("Risk (points)",   f"{risk:.6f}")
    _result_line("Reward (points)", f"{reward:.6f}")
    col = C_SUCCESS if rr >= 2.0 else (C_WARN if rr >= 1.0 else C_LOSS)
    _result_line("R:R Ratio",       f"{col}1 : {rr:.2f}{C_RESET}")
    rating = "✔ Excellent" if rr >= 3 else ("✔ Good" if rr >= 2 else ("~ Fair" if rr >= 1 else "✖ Poor"))
    _result_line("Rating",          f"{col}{rating}{C_RESET}")
    print(C_BORDER + "  └──────────────────────────────────────────┘")
    pause()


def _pip_value():
    clear()
    print_logo()
    section_header("PIP VALUE CALCULATOR")
    print(f"  {C_DIM}Calculate pip value for Forex pairs.{C_RESET}\n")

    lot_size    = prompt_float("Lot size (standard lot = 100000)", 1.0)
    pip_size    = prompt_float("Pip size (0.0001 for most pairs, 0.01 for JPY)", 0.0001)
    quote_price = prompt_float("Current quote price")

    if quote_price == 0:
        error("Quote price cannot be zero.")
        pause()
        return

    pip_value = (pip_size / quote_price) * lot_size

    print()
    print(C_BORDER + "  ┌──────────────────────────────────────────┐")
    print(C_BORDER + "  │           CALCULATION RESULTS             │")
    print(C_BORDER + "  ├──────────────────────────────────────────┤")
    _result_line("Lot Size",    f"{lot_size:.2f}")
    _result_line("Pip Size",    f"{pip_size:.6f}")
    _result_line("Pip Value",   f"{C_PROFIT}{pip_value:,.6f} per pip{C_RESET}")
    print(C_BORDER + "  └──────────────────────────────────────────┘")
    pause()


def _result_line(label, value):
    print(C_BORDER + f"  │  {C_HEADER}{label:<18}{C_RESET}  {value:<20}  {C_BORDER}│")
