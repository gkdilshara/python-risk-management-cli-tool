# ============================================================
#  ui/screens/accounts.py — Account Management Screen
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from tabulate import tabulate
from models.account  import AccountModel
from models.risk_rule import RiskRuleModel
from ui.helpers import *
from ui.theme  import *


def screen_accounts():
    while True:
        choice = arrow_menu(
            "ACCOUNT MANAGEMENT",
            [
                "📋  List All Accounts",
                "➕  Create New Account",
                "✏️   Edit Account Balance",
                "🗑️   Delete Account",
                "🔙  Back to Main Menu",
            ],
        )

        if choice == 0:   _list_accounts()
        elif choice == 1: _create_account()
        elif choice == 2: _edit_balance()
        elif choice == 3: _delete_account()
        elif choice in (4, -1): break


def _list_accounts():
    clear()
    print_logo()
    section_header("ALL ACCOUNTS")
    rows = AccountModel.all()
    if not rows:
        warning("No accounts found. Create one first.")
    else:
        table = [
            [r["id"], r["name"], r["currency"], f"{float(r['balance']):,.2f}", r["created_at"]]
            for r in rows
        ]
        print(C_BORDER + tabulate(
            table,
            headers=["ID", "Name", "Currency", "Balance", "Created"],
            tablefmt="rounded_outline",
        ))
    pause()


def _create_account():
    clear()
    print_logo()
    section_header("CREATE NEW ACCOUNT")
    name     = prompt("Account name")
    if not name:
        error("Name cannot be empty.")
        pause()
        return
    currency = prompt("Currency", "USD")
    balance  = prompt_float("Starting balance", 10000.00)

    acc_id = AccountModel.create(name, balance, currency.upper())
    RiskRuleModel.create_defaults(acc_id)
    info(f"Account '{name}' created with ID {acc_id}.")
    pause()


def _edit_balance():
    clear()
    print_logo()
    section_header("EDIT ACCOUNT BALANCE")
    acc_id  = prompt_int("Account ID")
    acc     = AccountModel.get(acc_id)
    if not acc:
        error("Account not found.")
        pause()
        return
    print(f"\n  Current balance: {C_HEADER}{float(acc['balance']):,.2f} {acc['currency']}{C_RESET}\n")
    new_bal = prompt_float("New balance")
    AccountModel.update_balance(acc_id, new_bal)
    info(f"Balance updated to {new_bal:,.2f}.")
    pause()


def _delete_account():
    clear()
    print_logo()
    section_header("DELETE ACCOUNT")
    acc_id = prompt_int("Account ID to delete")
    acc    = AccountModel.get(acc_id)
    if not acc:
        error("Account not found.")
        pause()
        return
    confirm = prompt(f"Delete '{acc['name']}'? This removes ALL trades! (yes/no)", "no")
    if confirm.lower() == "yes":
        AccountModel.delete(acc_id)
        info("Account deleted.")
    else:
        warning("Cancelled.")
    pause()
