# ============================================================
#  ui/screens/dashboard.py — Account Dashboard / Stats
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from tabulate import tabulate
from models.account   import AccountModel
from models.trade     import TradeModel
from models.risk_rule import RiskRuleModel
from ui.helpers import *
from ui.theme   import *
from datetime   import date


def screen_dashboard():
    accounts = AccountModel.all()
    if not accounts:
        clear()
        print_logo()
        section_header("DASHBOARD")
        warning("No accounts found. Please create an account first.")
        pause()
        return

    names  = [f"[{a['id']}]  {a['name']}  ({a['currency']} {float(a['balance']):,.2f})" for a in accounts]
    names += ["🔙  Back"]
    idx    = arrow_menu("DASHBOARD — SELECT ACCOUNT", names)

    if idx < 0 or idx == len(accounts):
        return

    acc = accounts[idx]
    _show_dashboard(acc)


def _show_dashboard(acc):
    clear()
    print_logo()
    section_header(f"DASHBOARD  ──  {acc['name']}")

    # ── Summary stats ────────────────────────────────────────
    all_trades    = TradeModel.all(acc["id"])
    open_trades   = [t for t in all_trades if t["status"] == "OPEN"]
    closed_trades = [t for t in all_trades if t["status"] == "CLOSED"]

    wins   = [t for t in closed_trades if t["pnl"] and float(t["pnl"]) > 0]
    losses = [t for t in closed_trades if t["pnl"] and float(t["pnl"]) <= 0]
    total_pnl  = sum(float(t["pnl"]) for t in closed_trades if t["pnl"])
    daily_pnl  = TradeModel.daily_pnl(acc["id"])
    win_rate   = (len(wins) / len(closed_trades) * 100) if closed_trades else 0

    balance = float(acc["balance"])
    rule    = RiskRuleModel.get(acc["id"])

    # ── Account card ─────────────────────────────────────────
    bal_col = C_SUCCESS if balance > 0 else C_LOSS
    print(f"  {C_HEADER}Account :{C_RESET}  {acc['name']}")
    print(f"  {C_HEADER}Currency:{C_RESET}  {acc['currency']}")
    print(f"  {C_HEADER}Balance :{C_RESET}  {bal_col}{balance:,.2f}{C_RESET}")
    print()

    # ── Trade stats ──────────────────────────────────────────
    pnl_col  = C_PROFIT if total_pnl >= 0 else C_LOSS
    dpnl_col = C_PROFIT if daily_pnl >= 0 else C_LOSS

    stats = [
        ["Total Trades",    len(all_trades)],
        ["Open Trades",     len(open_trades)],
        ["Closed Trades",   len(closed_trades)],
        ["Winning Trades",  f"{C_PROFIT}{len(wins)}{C_RESET}"],
        ["Losing Trades",   f"{C_LOSS}{len(losses)}{C_RESET}"],
        ["Win Rate",        f"{win_rate:.1f}%"],
        ["Total P&L",       f"{pnl_col}{total_pnl:+,.2f}{C_RESET}"],
        ["Today's P&L",     f"{dpnl_col}{daily_pnl:+,.2f}{C_RESET}"],
    ]
    print(C_BORDER + tabulate(stats, headers=["Metric", "Value"], tablefmt="rounded_outline"))
    print()

    # ── Risk rules snapshot ──────────────────────────────────
    if rule:
        daily_loss_pct = (abs(daily_pnl) / balance * 100) if balance > 0 and daily_pnl < 0 else 0
        open_count     = len(open_trades)
        dl_col = C_LOSS if daily_loss_pct >= float(rule["max_daily_loss"]) else C_SUCCESS
        ot_col = C_LOSS if open_count    >= rule["max_open_trades"]        else C_SUCCESS

        risk_rows = [
            ["Max Risk/Trade",    f"{float(rule['max_risk_per_trade']):.2f}%",  "—"],
            ["Max Daily Loss",    f"{float(rule['max_daily_loss']):.2f}%",
             f"{dl_col}{daily_loss_pct:.2f}%{C_RESET}"],
            ["Max Open Trades",   str(rule["max_open_trades"]),
             f"{ot_col}{open_count}{C_RESET}"],
            ["Max Position Size", f"{float(rule['max_position_size']):.2f}%",   "—"],
        ]
        section_header("RISK RULES STATUS")
        print(C_BORDER + tabulate(
            risk_rows,
            headers=["Rule", "Limit", "Current"],
            tablefmt="rounded_outline",
        ))
        print()

    # ── Open trades snapshot ─────────────────────────────────
    if open_trades:
        section_header("OPEN POSITIONS")
        table = [
            [t["id"], t["symbol"], t["trade_type"],
             f"{float(t['quantity']):.4f}",
             f"{float(t['entry_price']):.4f}",
             f"{float(t['stop_loss']):.4f}"   if t["stop_loss"]  else "—",
             f"{float(t['take_profit']):.4f}" if t["take_profit"] else "—",
             ]
            for t in open_trades
        ]
        print(C_BORDER + tabulate(
            table,
            headers=["ID", "Symbol", "Type", "Qty", "Entry", "Stop Loss", "Take Profit"],
            tablefmt="rounded_outline",
        ))

    pause()
