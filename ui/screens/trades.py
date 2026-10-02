# ============================================================
#  ui/screens/trades.py — Trade Management Screen
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from tabulate import tabulate
from models.account        import AccountModel
from models.trade          import TradeModel
from models.session        import SessionModel
from models.risk_rule      import RiskRuleModel
from models.journal        import JournalModel
from models.smart_stake    import SmartStakeEngine
from ui.helpers import *
from ui.theme   import *
from datetime   import date


def screen_trades():
    while True:
        choice = arrow_menu(
            "TRADE MANAGEMENT",
            [
                "📂  Select Account & View Trades",
                "➕  Open / Record New Trade",
                "🔒  Close Trade (Record Exit / Option Outcome)",
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
    names = [
        f"[{a['id']}]  {a['name']}  [{a.get('account_type', 'STANDARD')}]  ({a['currency']} {float(a['balance']):,.2f})"
        for a in accounts
    ]
    names.append("🔙  Cancel")
    idx = arrow_menu("SELECT ACCOUNT", names)
    if idx < 0 or idx == len(accounts):
        return None
    return accounts[idx]


def _select_session_for_account(account_id: int):
    """Optionally select an active trading session for an account."""
    sessions = SessionModel.get_active(account_id)
    if not sessions:
        return None

    names = [f"[{s['id']}]  {s['session_name']} ({s['trading_method']})" for s in sessions]
    names.append("🌐  No Session (Standalone Trade)")
    idx = arrow_menu("SELECT SESSION FOR THIS TRADE", names)

    if idx < 0 or idx == len(sessions):
        return None
    return sessions[idx]


def _prompt_smart_stake_selector(
    account_id: int,
    session_id: int = None,
    payout_pct: float = 95.0,
    currency: str = "USD",
) -> float:
    """
    Present the Smart Advanced Stake Suggestion Assistant with 5 Safety Levels
    and Session Target Profit / Willing Trades guidance.
    """
    sugg = SmartStakeEngine.get_suggestions(account_id, session_id, payout_pct)

    clear()
    print_logo()
    section_header("🧠 SMART ADVANCED STAKE ASSISTANT (5 SAFETY LEVELS)")

    print(f"  {C_HEADER}Capital Basis:{C_RESET}     ${sugg['base_capital']:,.2f} {currency}  ({sugg['capital_source']})")
    print(f"  {C_HEADER}Max Risk Limit:{C_RESET}    {sugg['max_risk_pct']:.1f}%")

    if sugg.get("target_profit") is not None:
        print(f"  {C_HEADER}Session Goal:{C_RESET}      Target Profit: ${sugg['target_profit']:,.2f} {currency}")

    if sugg.get("max_planned_trades") is not None:
        print(f"  {C_HEADER}Willing Trades:{C_RESET}    {sugg['max_planned_trades']} trades max")

    print()

    if sugg.get("target_status_note"):
        info(sugg["target_status_note"])
        print()

    if sugg.get("recommendation_note"):
        warning(sugg["recommendation_note"])
        print()

    menu_items = []

    # If optimal target stake calculated, offer it first as option 0
    if sugg.get("target_optimal_stake") is not None and sugg["target_optimal_stake"] > 0:
        opt_stake  = sugg["target_optimal_stake"]
        opt_profit = round(opt_stake * (payout_pct / 100.0), 2)
        menu_items.append(
            f"🎯 Target Goal Optimal Stake ── ${opt_stake:,.2f}  (Est. Win: +${opt_profit:,.2f}) [SESSION GOAL]"
        )

    for item in sugg["levels"]:
        rec_str    = " ⭐ RECOMMENDED" if item["is_recommended"] else ""
        breach_str = " (⚠️ BREACHES RULE)" if item["is_breach"] else ""
        menu_items.append(
            f"{item['badge']} {item['name']} ({item['pct']:.1f}%) ── ${item['stake_amount']:,.2f}  "
            f"(Est. Win: +${item['payout_profit']:,.2f}){rec_str}{breach_str}"
        )

    menu_items.append("✏️   Enter Custom Stake Amount Manually...")
    menu_items.append("🔙  Cancel Trade")

    subtitle_text = f"Select safety level, optimal target stake, or custom amount (Base: ${sugg['base_capital']:,.2f} {currency})"
    choice = arrow_menu("SMART STAKE SUGGESTIONS", menu_items, subtitle=subtitle_text)

    if choice < 0 or choice == len(menu_items) - 1:
        return None

    if choice == len(menu_items) - 2:
        return prompt_float("Enter Custom Stake Amount ($)")

    if sugg.get("target_optimal_stake") is not None and sugg["target_optimal_stake"] > 0:
        if choice == 0:
            opt_s = sugg["target_optimal_stake"]
            info(f"Selected Target Goal Optimal Stake: ${opt_s:,.2f} {currency}")
            return opt_s
        chosen_level = sugg["levels"][choice - 1]
    else:
        chosen_level = sugg["levels"][choice]

    info(f"Selected {chosen_level['name']} ({chosen_level['pct']:.1f}%): ${chosen_level['stake_amount']:,.2f} {currency}")
    return chosen_level["stake_amount"]


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

    acc_type = acc.get("account_type", "STANDARD")

    while True:
        status_choice = arrow_menu(
            f"TRADES — {acc['name']} [{acc_type}]",
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
                res_str = r.get("option_result") or "—"
                if res_str == "WIN":
                    res_str = f"{C_PROFIT}WIN{C_RESET}"
                elif res_str == "LOSS":
                    res_str = f"{C_LOSS}LOSS{C_RESET}"

                table.append([
                    r["id"],
                    r.get("session_id") or "—",
                    r["symbol"],
                    r["trade_type"],
                    f"{float(r['quantity']):.4f}",
                    f"{float(r['entry_price']):.4f}",
                    f"{float(r['exit_price']):.4f}" if r["exit_price"] else "—",
                    res_str,
                    pnl_str,
                    r["status"],
                ])
            print(C_BORDER + tabulate(
                table,
                headers=["ID", "Sess#", "Symbol", "Type", "Stake/Qty", "Entry", "Exit", "Outcome", "P&L", "Status"],
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

    acc_type   = acc.get("account_type", "STANDARD")
    session    = _select_session_for_account(acc["id"])
    session_id = session["id"] if session else None

    clear()
    print_logo()
    section_header(f"OPEN NEW TRADE  [{acc['name']} - {acc_type}]")
    if session:
        print(f"  {C_HEADER}Session:{C_RESET} {session['session_name']} ({session['trading_method']})\n")
    print(f"  {C_HEADER}Balance:{C_RESET} {float(acc['balance']):,.2f} {acc['currency']}\n")

    if acc_type == "DERIV_OPTION":
        # ── DERIV OPTION TRADE FLOW ─────────────────────────────
        symbol = prompt("Symbol / Market (e.g. Volatility 100 Index, EURUSD)", "Volatility 100 Index").upper()

        type_idx = arrow_menu("Deriv Option Contract Type", ["📈  RISE (Call)", "📉  FALL (Put)", "🔙  Cancel"])
        if type_idx in (2, -1):
            return
        trade_type = "RISE" if type_idx == 0 else "FALL"

        default_payout = float(session["payout_percentage"]) if (session and session["payout_percentage"]) else 95.0
        payout_pct = prompt_float("Payout Percentage (%)", default_payout)

        # 🧠 SMART STAKE SUGGESTION ENGINE ASSISTANT (with Target Profit & Willing Trades logic)
        stake = _prompt_smart_stake_selector(
            account_id=acc["id"],
            session_id=session_id,
            payout_pct=payout_pct,
            currency=acc["currency"],
        )
        if stake is None:
            warning("Trade creation cancelled.")
            pause()
            return

        # Ask if trade outcome is known now (or keep open)
        outcome_idx = arrow_menu(
            "Record Option Outcome Now?",
            [
                "🏆  WIN   (Recorded immediately with payout profit)",
                "💀  LOSS  (Recorded immediately as loss)",
                "⏳  OPEN  (Keep as open option trade)",
            ],
        )
        if outcome_idx == -1:
            return

        option_res = "WIN" if outcome_idx == 0 else ("LOSS" if outcome_idx == 1 else None)
        notes      = prompt("Notes (optional)", "")

        trade_id = TradeModel.create(
            account_id=acc["id"],
            symbol=symbol,
            trade_type=trade_type,
            quantity=stake,
            entry_price=stake,
            session_id=session_id,
            payout_percentage=payout_pct,
            option_result=option_res,
            notes=notes,
        )

        if option_res:
            pnl_val = round(stake * (payout_pct / 100.0), 2) if option_res == "WIN" else -round(stake, 2)
            col     = C_PROFIT if pnl_val >= 0 else C_LOSS
            info(f"Deriv Option Trade #{trade_id} [{trade_type}] recorded as {option_res}! P&L: {col}{pnl_val:+,.2f}{C_RESET}")
        else:
            info(f"Deriv Option Trade #{trade_id} [{trade_type}] opened for ${stake:.2f}.")

        JournalModel.upsert(acc["id"], date.today())

    else:
        # ── STANDARD TRADING FLOW ────────────────────────────────
        symbol = prompt("Symbol (e.g. BTCUSD, AAPL, EURUSD)").upper()
        if not symbol:
            error("Symbol cannot be empty.")
            pause()
            return

        trade_type_idx = arrow_menu("Trade Type", ["📈  BUY  (Long)", "📉  SELL (Short)", "🔙  Cancel"])
        if trade_type_idx in (2, -1):
            return
        trade_type = "BUY" if trade_type_idx == 0 else "SELL"

        # 🧠 SMART STAKE SUGGESTION ENGINE ASSISTANT
        suggested_stake = _prompt_smart_stake_selector(
            account_id=acc["id"],
            session_id=session_id,
            payout_pct=100.0,
            currency=acc["currency"],
        )

        if suggested_stake is None:
            warning("Trade creation cancelled.")
            pause()
            return

        qty         = prompt_float("Quantity / Lot size / Position Value", suggested_stake)
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
            account_id=acc["id"],
            symbol=symbol,
            trade_type=trade_type,
            quantity=qty,
            entry_price=entry_price,
            stop_loss=sl,
            take_profit=tp,
            session_id=session_id,
            notes=notes,
        )
        info(f"Trade #{trade_id} opened: {trade_type} {qty} {symbol} @ {entry_price}")

    pause()


def _close_trade():
    clear()
    print_logo()
    section_header("CLOSE / RESOLVE TRADE")
    trade_id = prompt_int("Trade ID to close")
    trade    = TradeModel.get(trade_id)
    if not trade:
        error("Trade not found.")
        pause()
        return
    if trade["status"] != "OPEN":
        error(f"Trade #{trade_id} is already {trade['status']}.")
        pause()
        return

    trade_type = trade["trade_type"]

    if trade_type in ("RISE", "FALL"):
        # Option trade close
        print(f"\n  {C_HEADER}Option Contract:{C_RESET} {trade['trade_type']} ${float(trade['quantity']):,.2f} on {trade['symbol']}\n")
        res_idx = arrow_menu("Option Result", ["🏆  WIN  (Full Payout)", "💀  LOSS (Stake Lost)", "🔙  Cancel"])
        if res_idx in (2, -1):
            return

        result_str = "WIN" if res_idx == 0 else "LOSS"
        pnl, err = TradeModel.close_option(trade_id, result_str)
        if err:
            error(err)
        else:
            col = C_PROFIT if pnl >= 0 else C_LOSS
            info(f"Option Trade #{trade_id} closed as {result_str}. P&L: {col}{pnl:+,.2f}{C_RESET}")
            JournalModel.upsert(trade["account_id"], date.today())
    else:
        # Standard trade close
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
