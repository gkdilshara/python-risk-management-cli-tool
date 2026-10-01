# ============================================================
#  ui/screens/sessions.py — Trading Sessions Management
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from tabulate import tabulate
from datetime import datetime
from models.account import AccountModel
from models.session import SessionModel
from models.trade   import TradeModel
from ui.helpers import *
from ui.theme   import *


def screen_sessions():
    while True:
        choice = arrow_menu(
            "TRADING SESSIONS MANAGEMENT",
            [
                "📋  List All Sessions",
                "➕  Create New Session",
                "📊  View Session Stats & Trades",
                "🔒  Complete Active Session",
                "❌  Cancel Session",
                "🔙  Back to Main Menu",
            ],
        )

        if choice == 0:   _list_sessions()
        elif choice == 1: _create_session()
        elif choice == 2: _view_session_stats()
        elif choice == 3: _complete_session()
        elif choice == 4: _cancel_session()
        elif choice in (5, -1): break


def _select_account():
    accounts = AccountModel.all()
    if not accounts:
        error("No accounts found. Create an account first.")
        pause()
        return None
    names = [
        f"[{a['id']}]  {a['name']}  [{a.get('account_type', 'STANDARD')}]  ({a['currency']} {float(a['balance']):,.2f})"
        for a in accounts
    ]
    names.append("🔙  Cancel")
    idx = arrow_menu("SELECT ACCOUNT FOR SESSION", names)
    if idx < 0 or idx == len(accounts):
        return None
    return accounts[idx]


def _list_sessions():
    clear()
    print_logo()
    section_header("TRADING SESSIONS")

    sessions = SessionModel.all()
    if not sessions:
        warning("No trading sessions found.")
    else:
        table = []
        for s in sessions:
            status_col = C_SUCCESS if s["status"] == "ACTIVE" else (C_WARN if s["status"] == "COMPLETED" else C_DIM)
            payout_str = f"{float(s['payout_percentage']):.1f}%" if s["payout_percentage"] else "—"
            table.append([
                s["id"],
                s["account_name"],
                s["session_name"],
                s["trading_method"],
                payout_str,
                f"{float(s['reserved_stake_capital']):,.2f}",
                f"{status_col}{s['status']}{C_RESET}",
                s["created_at"],
            ])

        print(C_BORDER + tabulate(
            table,
            headers=["ID", "Account", "Session Name", "Method", "Payout %", "Reserved Stake", "Status", "Created At"],
            tablefmt="rounded_outline",
        ))
    pause()


def _create_session():
    acc = _select_account()
    if not acc:
        return

    acc_type = acc.get("account_type", "STANDARD")
    created_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    clear()
    print_logo()
    section_header(f"NEW TRADING SESSION  [{acc['name']} - {acc_type}]")
    print(f"  {C_HEADER}Auto-Fetched Created Timestamp:{C_RESET} {C_SUCCESS}{created_timestamp}{C_RESET}\n")

    trading_method = "STANDARD"
    payout_pct = None

    if acc_type == "DERIV_OPTION":
        # Select Trading Method for Option Account
        method_idx = arrow_menu(
            "SELECT TRADING METHOD",
            [
                "📈📉  RISE / FALL  (Rise/Fall Option Method)",
                "🔙   Cancel",
            ],
            subtitle="Choose option contract method for this session",
        )
        if method_idx in (1, -1):
            return
        trading_method = "RISE_FALL"

        # Ask for Payout Percentage
        payout_pct = prompt_float("Payout Percentage (%)", 95.0)

        # Ask for Reserved Stake Capital
        reserved_stake = prompt_float("Reserved Stake Capital ($)", 500.00)
    else:
        # Standard Account
        trading_method = "STANDARD"
        payout_pct = None
        reserved_stake = prompt_float("Reserved Session Capital ($)", 1000.00)

    # Session Name with default
    default_name = f"{trading_method} Session - {created_timestamp}"
    session_name = prompt("Session Name", default_name)
    notes        = prompt("Session Notes (optional)", "")

    # ── CONFIRMATION STEP ─────────────────────────────────────
    clear()
    print_logo()
    section_header("CONFIRMATION: TRADING SESSION CREATION")

    print(C_BORDER + "  ┌───────────────────────────────────────────────────────────┐")
    print(C_BORDER + f"  │  {C_HEADER}Account:{C_RESET}          {acc['name']} [{acc_type}]")
    print(C_BORDER + f"  │  {C_HEADER}Session Name:{C_RESET}     {session_name}")
    print(C_BORDER + f"  │  {C_HEADER}Trading Method:{C_RESET}   {trading_method}")
    print(C_BORDER + f"  │  {C_HEADER}Created At:{C_RESET}       {created_timestamp} (Auto-fetched)")
    if payout_pct is not None:
        print(C_BORDER + f"  │  {C_HEADER}Payout %:{C_RESET}         {payout_pct:.2f}%")
    print(C_BORDER + f"  │  {C_HEADER}Reserved Capital:{C_RESET} ${reserved_stake:,.2f} {acc['currency']}")
    if notes:
        print(C_BORDER + f"  │  {C_HEADER}Notes:{C_RESET}            {notes}")
    print(C_BORDER + "  └───────────────────────────────────────────────────────────┘\n")

    confirm = prompt("Confirm creation of this trading session? (yes/no)", "yes")
    if confirm.lower() in ("y", "yes"):
        session_id = SessionModel.create(
            acc["id"],
            session_name=session_name,
            trading_method=trading_method,
            payout_percentage=payout_pct,
            reserved_stake_capital=reserved_stake,
            notes=notes,
        )
        info(f"Trading Session #{session_id} '{session_name}' created successfully!")
    else:
        warning("Session creation cancelled.")
    pause()


def _view_session_stats():
    sessions = SessionModel.all()
    if not sessions:
        clear()
        print_logo()
        section_header("SESSION STATS")
        warning("No trading sessions found.")
        pause()
        return

    names = [
        f"[{s['id']}]  {s['session_name']} ({s['trading_method']}) - {s['status']}"
        for s in sessions
    ]
    names.append("🔙  Back")
    idx = arrow_menu("SELECT SESSION TO VIEW", names)
    if idx < 0 or idx == len(sessions):
        return

    session_id = sessions[idx]["id"]
    stats = SessionModel.get_stats(session_id)
    if not stats:
        error("Could not fetch session statistics.")
        pause()
        return

    s = stats["session"]
    clear()
    print_logo()
    section_header(f"SESSION #{s['id']} STATS — {s['session_name']}")

    pnl_col = C_PROFIT if stats["total_pnl"] >= 0 else C_LOSS
    rem_col = C_SUCCESS if stats["remaining_capital"] >= 0 else C_LOSS

    summary_rows = [
        ["Session ID",         s["id"]],
        ["Account",            f"{s['account_name']} [{s['account_type']}]"],
        ["Trading Method",     s["trading_method"]],
        ["Created At",         s["created_at"]],
        ["Payout %",           f"{float(s['payout_percentage']):.1f}%" if s["payout_percentage"] else "—"],
        ["Reserved Capital",   f"{stats['reserved_capital']:,.2f} {s['currency']}"],
        ["Total Staked",       f"{stats['total_staked']:,.2f} {s['currency']}"],
        ["Total Trades",       stats["total_trades"]],
        ["Wins / Losses",      f"{C_PROFIT}{stats['wins']}{C_RESET} / {C_LOSS}{stats['losses']}{C_RESET}"],
        ["Win Rate",           f"{stats['win_rate']:.1f}%"],
        ["Session P&L",        f"{pnl_col}{stats['total_pnl']:+,.2f} {s['currency']}{C_RESET}"],
        ["Remaining Capital",  f"{rem_col}{stats['remaining_capital']:,.2f} {s['currency']}{C_RESET}"],
        ["Status",             s["status"]],
    ]

    print(C_BORDER + tabulate(summary_rows, headers=["Metric", "Value"], tablefmt="rounded_outline"))
    print()

    # View trades in session
    trades = TradeModel.all(s["account_id"], session_id=s["id"])
    if trades:
        section_header("TRADES IN THIS SESSION")
        table = []
        for t in trades:
            pnl_val = float(t["pnl"]) if t["pnl"] is not None else 0.0
            col = C_PROFIT if pnl_val >= 0 else C_LOSS
            table.append([
                t["id"],
                t["symbol"],
                t["trade_type"],
                f"{float(t['quantity']):.4f}",
                f"{float(t['entry_price']):.4f}",
                t.get("option_result") or "—",
                f"{col}{pnl_val:+,.2f}{C_RESET}",
                t["status"],
            ])
        print(C_BORDER + tabulate(
            table,
            headers=["ID", "Symbol", "Type", "Stake/Qty", "Price", "Result", "P&L", "Status"],
            tablefmt="rounded_outline",
        ))

    pause()


def _complete_session():
    sessions = SessionModel.all(status="ACTIVE")
    if not sessions:
        clear()
        print_logo()
        section_header("COMPLETE SESSION")
        warning("No active trading sessions found.")
        pause()
        return

    names = [f"[{s['id']}]  {s['session_name']} ({s['trading_method']})" for s in sessions]
    names.append("🔙  Cancel")
    idx = arrow_menu("SELECT ACTIVE SESSION TO COMPLETE", names)
    if idx < 0 or idx == len(sessions):
        return

    session_id = sessions[idx]["id"]
    notes = prompt("Final completion notes (optional)", "")
    SessionModel.complete(session_id, notes)
    info(f"Session #{session_id} marked as COMPLETED.")
    pause()


def _cancel_session():
    sessions = SessionModel.all(status="ACTIVE")
    if not sessions:
        clear()
        print_logo()
        section_header("CANCEL SESSION")
        warning("No active trading sessions found.")
        pause()
        return

    names = [f"[{s['id']}]  {s['session_name']} ({s['trading_method']})" for s in sessions]
    names.append("🔙  Cancel")
    idx = arrow_menu("SELECT SESSION TO CANCEL", names)
    if idx < 0 or idx == len(sessions):
        return

    session_id = sessions[idx]["id"]
    confirm = prompt(f"Cancel session #{session_id}? (yes/no)", "no")
    if confirm.lower() == "yes":
        SessionModel.cancel(session_id)
        info(f"Session #{session_id} cancelled.")
    else:
        warning("Cancelled action.")
    pause()
