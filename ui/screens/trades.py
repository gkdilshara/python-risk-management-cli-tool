# ============================================================
#  ui/screens/trades.py — Trade Management Screen
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from tabulate import tabulate
from models.account   import AccountModel
from models.trade     import TradeModel
from models.risk_rule import RiskRuleModel
from models.journal   import JournalModel
from ui.helpers import *
from ui.theme   import *
from datetime   import date


def screen_trades():
    while True:
        choice = arrow_menu(
            "TRADE MANAGEMENT",
            [
                "📂  Select Account & View Trades",
                "➕  Open New Trade",
                "🔒  Close Trade (Record Exit)",
                "❌  Cancel Trade",
                "🔙  Back to Main Menu",
            ],
        )

        if choice == 0:   _view_trades()
        elif choice == 1: _open_trade()
        elif choice == 2: _close_trade()
        elif choice == 3: _cancel_trade()
        elif choice in (4, -1): break


# ── helpers ──────────────────────────────────────────────────

def _select_account():
    accounts = AccountModel.all()
    if not accounts:
        error("No accounts found. Create an account first.")
        pause()
        return None
    names  = [f"[{a['id']}]  {a['name']}  ({a['currency']} {float(a['balance']):,.2f})" for a in accounts]
    names += ["🔙  Cancel"]
    idx    = arrow_menu("SELECT ACCOUNT", names)
    if idx < 0 or idx == len(accounts):
        return None
    return accounts[idx]


def _pnl_color(pnl):
    if pnl is None:
        return C_NEUTRAL + "  —  "
    val = float(pnl)
    col = C_PROFIT if val >= 0 else C_LOSS
    return col + f"{val:+,.2f}"


def _view_trades():
    acc = _select_account()
    if not acc:
        return

    while True:
        status_choice = arrow_menu(
            f"TRADES — {acc['name']}",
            ["🟢  Open Trades", "🔵  Closed Trades", "⚪  All Trades", "🔙  Back"],
            subtitle=f"Balance: {float(acc['balance']):,.2f} {acc['currency']}",
        )
        if status_choice == 3 or status_choice == -1:
            break

        status_map = {0: "OPEN", 1: "CLOSED", 2: None}
        status     = status_map[status_choice]

        clear()
        print_logo()
        section_header(f"TRADES  [{acc['name']}]  {status or 'ALL'}")

        rows = TradeModel.all(acc["id"], status)
        if not rows:
            warning("No trades found for this filter.")
        else:
            table = []
            for r in rows:
                pnl_str = _pnl_color(r["pnl"]) + C_RESET
                table.append([
                    r["id"],
                    r["symbol"],
                    r["trade_type"],
                    f"{float(r['quantity']):.4f}",
                    f"{float(r['entry_price']):.4f}",
                    f"{float(r['exit_price']):.4f}" if r["exit_price"] else "—",
                    f"{float(r['stop_loss']):.4f}"   if r["stop_loss"]  else "—",
                    f"{float(r['take_profit']):.4f}" if r["take_profit"] else "—",
                    pnl_str,
                    r["status"],
                ])
            print(C_BORDER + tabulate(
                table,
                headers=["ID", "Symbol", "Type", "Qty", "Entry", "Exit", "SL", "TP", "P&L", "Status"],
                tablefmt="rounded_outline",
            ))
        pause()


def _check_risk(acc, symbol, qty, entry_price, stop_loss):
    """Return (ok, warnings) based on configured risk rules."""
    rule = RiskRuleModel.get(acc["id"])
    if not rule:
        return True, []

    balance = float(acc["balance"])
    warns   = []
    ok      = True

    # Max open trades
    open_count = TradeModel.open_trades_count(acc["id"])
    if open_count >= rule["max_open_trades"]:
        warns.append(f"Max open trades reached ({rule['max_open_trades']})")
        ok = False

    # Position size check
    position_val = float(qty) * float(entry_price)
    pos_pct      = (position_val / balance * 100) if balance > 0 else 0
    if pos_pct > float(rule["max_position_size"]):
        warns.append(
            f"Position size {pos_pct:.1f}% exceeds limit {rule['max_position_size']}%"
        )
        ok = False

    # Risk per trade check (using stop-loss)
    if stop_loss:
        risk_amount = abs(float(entry_price) - float(stop_loss)) * float(qty)
        risk_pct    = (risk_amount / balance * 100) if balance > 0 else 0
        if risk_pct > float(rule["max_risk_per_trade"]):
            warns.append(
                f"Trade risk {risk_pct:.1f}% exceeds limit {rule['max_risk_per_trade']}%"
            )
            ok = False

    # Daily loss check
    daily_pnl = TradeModel.daily_pnl(acc["id"])
    daily_pct  = (abs(daily_pnl) / balance * 100) if balance > 0 and daily_pnl < 0 else 0
    if daily_pct >= float(rule["max_daily_loss"]):
        warns.append(
            f"Daily loss limit {rule['max_daily_loss']}% already reached!"
        )
        ok = False

    return ok, warns


def _open_trade():
    acc = _select_account()
    if not acc:
        return

    clear()
    print_logo()
    section_header(f"OPEN NEW TRADE  [{acc['name']}]")
    print(f"  Balance: {C_HEADER}{float(acc['balance']):,.2f} {acc['currency']}{C_RESET}\n")

    symbol      = prompt("Symbol (e.g. BTCUSD, AAPL, EURUSD)").upper()
    if not symbol:
        error("Symbol cannot be empty.")
        pause()
        return

    trade_type_idx = arrow_menu("Trade Type", ["📈  BUY  (Long)", "📉  SELL (Short)", "🔙  Cancel"])
    if trade_type_idx == 2 or trade_type_idx == -1:
        return
    trade_type = "BUY" if trade_type_idx == 0 else "SELL"

    qty         = prompt_float("Quantity / Lot size")
    entry_price = prompt_float("Entry price")
    stop_loss   = prompt("Stop loss price (blank to skip)")
    take_profit = prompt("Take profit price (blank to skip)")
    notes       = prompt("Notes (optional)", "")

    sl = float(stop_loss) if stop_loss else None
    tp = float(take_profit) if take_profit else None

    # Risk validation
    ok, warns = _check_risk(acc, symbol, qty, entry_price, sl)

    if warns:
        print()
        for w in warns:
            warning(w)

    if not ok:
        print()
        override = prompt("Risk limits breached. Override and open anyway? (yes/no)", "no")
        if override.lower() != "yes":
            warning("Trade cancelled.")
            pause()
            return

    trade_id = TradeModel.create(
        acc["id"], symbol, trade_type, qty, entry_price, sl, tp, notes
    )
    info(f"Trade #{trade_id} opened: {trade_type} {qty} {symbol} @ {entry_price}")
    pause()


def _close_trade():
    clear()
    print_logo()
    section_header("CLOSE TRADE")
    trade_id   = prompt_int("Trade ID to close")
    trade      = TradeModel.get(trade_id)
    if not trade:
        error("Trade not found.")
        pause()
        return
    if trade["status"] != "OPEN":
        error(f"Trade #{trade_id} is already {trade['status']}.")
        pause()
        return

    print(
        f"\n  {C_HEADER}{trade['trade_type']} {float(trade['quantity']):.4f} {trade['symbol']}"
        f" @ {float(trade['entry_price']):.4f}{C_RESET}\n"
    )
    exit_price = prompt_float("Exit price")
    pnl, err   = TradeModel.close(trade_id, exit_price)
    if err:
        error(err)
    else:
        col = C_PROFIT if pnl >= 0 else C_LOSS
        info(f"Trade closed. P&L: {col}{pnl:+,.2f}{C_RESET}")
        # update journal
        JournalModel.upsert(trade["account_id"], date.today())
    pause()


def _cancel_trade():
    clear()
    print_logo()
    section_header("CANCEL TRADE")
    trade_id = prompt_int("Trade ID to cancel")
    trade    = TradeModel.get(trade_id)
    if not trade:
        error("Trade not found.")
        pause()
        return
    confirm = prompt(f"Cancel trade #{trade_id} ({trade['symbol']})? (yes/no)", "no")
    if confirm.lower() == "yes":
        TradeModel.cancel(trade_id)
        info(f"Trade #{trade_id} cancelled.")
    else:
        warning("Cancelled.")
    pause()
