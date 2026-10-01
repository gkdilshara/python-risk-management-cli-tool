# ============================================================
#  ui/screens/journal.py — Daily Journal Screen
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from tabulate import tabulate
from models.account import AccountModel
from models.journal import JournalModel
from ui.helpers import *
from ui.theme   import *
from datetime   import date


def screen_journal():
    while True:
        choice = arrow_menu(
            "TRADING JOURNAL",
            [
                "📅  View Journal History",
                "📝  Add / Update Today's Note",
                "🔄  Refresh Today's Entry",
                "🔙  Back to Main Menu",
            ],
        )

        if choice == 0:   _view_journal()
        elif choice == 1: _add_note()
        elif choice == 2: _refresh()
        elif choice in (3, -1): break


def _select_account():
    accounts = AccountModel.all()
    if not accounts:
        error("No accounts found.")
        pause()
        return None
    names  = [f"[{a['id']}]  {a['name']}" for a in accounts]
    names += ["🔙  Cancel"]
    idx    = arrow_menu("SELECT ACCOUNT", names)
    if idx < 0 or idx == len(accounts):
        return None
    return accounts[idx]


def _view_journal():
    acc = _select_account()
    if not acc:
        return

    clear()
    print_logo()
    section_header(f"JOURNAL HISTORY  [{acc['name']}]")

    rows = JournalModel.all(acc["id"])
    if not rows:
        warning("No journal entries found.")
    else:
        table = []
        for r in rows:
            pnl = float(r["gross_pnl"])
            col = C_PROFIT if pnl >= 0 else C_LOSS
            table.append([
                r["journal_date"],
                r["total_trades"],
                f"{C_PROFIT}{r['winning']}{C_RESET}",
                f"{C_LOSS}{r['losing']}{C_RESET}",
                f"{col}{pnl:+,.2f}{C_RESET}",
                (r["note"] or "")[:35],
            ])
        print(C_BORDER + tabulate(
            table,
            headers=["Date", "Trades", "Wins", "Losses", "Gross P&L", "Note"],
            tablefmt="rounded_outline",
        ))
    pause()


def _add_note():
    acc = _select_account()
    if not acc:
        return

    clear()
    print_logo()
    section_header(f"ADD NOTE — TODAY  [{acc['name']}]")

    note = prompt("Today's note / reflection")
    JournalModel.upsert(acc["id"], date.today(), note)
    info("Journal entry saved.")
    pause()


def _refresh():
    acc = _select_account()
    if not acc:
        return
    JournalModel.upsert(acc["id"], date.today())
    info("Today's journal entry refreshed from trade data.")
    pause()
