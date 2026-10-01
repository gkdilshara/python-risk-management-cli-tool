# ============================================================
#  ui/screens/risk.py — Risk Rules Screen
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from tabulate import tabulate
from models.account   import AccountModel
from models.risk_rule import RiskRuleModel
from ui.helpers import *
from ui.theme   import *


def screen_risk():
    while True:
        choice = arrow_menu(
            "RISK RULE MANAGEMENT",
            [
                "📋  View Risk Rules",
                "✏️   Edit Risk Rules",
                "🔙  Back to Main Menu",
            ],
        )

        if choice == 0:   _view_rules()
        elif choice == 1: _edit_rules()
        elif choice in (2, -1): break


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


def _view_rules():
    acc = _select_account()
    if not acc:
        return

    clear()
    print_logo()
    section_header(f"RISK RULES  [{acc['name']}]")

    rule = RiskRuleModel.get(acc["id"])
    if not rule:
        warning("No risk rules configured for this account.")
    else:
        table = [
            ["Max Risk Per Trade",  f"{float(rule['max_risk_per_trade']):.2f}%"],
            ["Max Daily Loss",       f"{float(rule['max_daily_loss']):.2f}%"],
            ["Max Open Trades",      rule["max_open_trades"]],
            ["Max Position Size",    f"{float(rule['max_position_size']):.2f}%"],
        ]
        print(C_BORDER + tabulate(table, headers=["Rule", "Value"], tablefmt="rounded_outline"))
    pause()


def _edit_rules():
    acc = _select_account()
    if not acc:
        return

    clear()
    print_logo()
    section_header(f"EDIT RISK RULES  [{acc['name']}]")

    rule = RiskRuleModel.get(acc["id"])
    defaults = rule if rule else {
        "max_risk_per_trade": 2.0,
        "max_daily_loss": 5.0,
        "max_open_trades": 5,
        "max_position_size": 10.0,
    }

    print(f"  {C_DIM}Leave blank to keep current value{C_RESET}\n")

    max_risk  = prompt_float("Max risk per trade (%)", float(defaults["max_risk_per_trade"]))
    max_daily = prompt_float("Max daily loss (%)", float(defaults["max_daily_loss"]))
    max_open  = prompt_int("Max open trades", int(defaults["max_open_trades"]))
    max_pos   = prompt_float("Max position size (%)", float(defaults["max_position_size"]))

    RiskRuleModel.update(acc["id"], max_risk, max_daily, max_open, max_pos)
    info("Risk rules saved.")
    pause()
