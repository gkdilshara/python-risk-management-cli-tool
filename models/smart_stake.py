# ============================================================
#  models/smart_stake.py — Smart Advanced Stake Suggestions Engine
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

from models.risk_rule import RiskRuleModel
from models.session   import SessionModel
from models.trade     import TradeModel


class SmartStakeEngine:
    """
    Computes 5 Safety Levels of Stake Suggestions dynamically based on:
      1. Available Capital (Account Balance or Active Session Remaining Capital)
      2. Configured Risk Rules (Max Risk %, Max Position Size %)
      3. Session Target Profit & Amount of Willing/Planned Trades
      4. Recent Win/Loss Streak & Performance Context
    """

    SAFETY_LEVELS = [
        {
            "level": 1,
            "name": "Level 1: Ultra Safe",
            "pct": 0.5,
            "badge": "🟢",
            "tag": "Capital Preservation",
            "desc": "Minimal drawdown impact. Maximizes survival during adverse market runs.",
        },
        {
            "level": 2,
            "name": "Level 2: Conservative",
            "pct": 1.5,
            "badge": "🛡️",
            "tag": "Safe Growth [RECOMMENDED]",
            "desc": "Balanced prudent risk. Ideal for consistent steady growth.",
        },
        {
            "level": 3,
            "name": "Level 3: Moderate",
            "pct": 3.0,
            "badge": "🟡",
            "tag": "Balanced Risk",
            "desc": "Standard risk sizing for high-confidence setups.",
        },
        {
            "level": 4,
            "name": "Level 4: Aggressive",
            "pct": 5.0,
            "badge": "🟧",
            "tag": "High Growth",
            "desc": "Accelerated capital growth. Higher drawdown exposure.",
        },
        {
            "level": 5,
            "name": "Level 5: Max Risk Limit",
            "pct": 10.0,
            "badge": "🔥",
            "tag": "Maximum Allowed Threshold",
            "desc": "Upper risk ceiling capped by account risk rules.",
        },
    ]

    @classmethod
    def get_suggestions(
        cls,
        account_id: int,
        session_id: int = None,
        payout_pct: float = 95.0,
        balance_override: float = None,
    ):
        """
        Generate stakeholder calculations for all 5 safety levels,
        smartly adapting to Session Target Profit and Willing Trades count.
        """
        capital_source = "Account Balance"
        base_capital   = 0.0

        target_profit      = None
        max_planned_trades = None
        current_pnl        = 0.0
        trades_count       = 0

        target_status_note   = None
        target_optimal_stake = None

        if session_id:
            stats = SessionModel.get_stats(session_id)
            if stats:
                base_capital       = max(float(stats["remaining_capital"]), 10.0)
                capital_source     = f"Session #{session_id} Remaining Capital"
                target_profit      = stats["target_profit"]
                max_planned_trades = stats["max_planned_trades"]
                current_pnl        = stats["total_pnl"]
                trades_count       = stats["total_trades"]

        if base_capital <= 0:
            from models.account import AccountModel
            acc = AccountModel.get(account_id)
            if balance_override is not None:
                base_capital = balance_override
            elif acc:
                base_capital = float(acc["balance"])
            capital_source = "Account Balance"

        base_capital = max(base_capital, 10.0)

        # Fetch Risk Rules
        rule = RiskRuleModel.get(account_id)
        max_risk_pct = float(rule["max_risk_per_trade"]) if rule else 5.0
        max_pos_pct  = float(rule["max_position_size"])  if rule else 10.0

        # Calculate Session Target & Planned Trades Smart Goal
        if target_profit is not None:
            if current_pnl >= target_profit:
                target_status_note = (
                    f"🏆  SESSION TARGET PROFIT REACHED! "
                    f"Current P&L: +${current_pnl:,.2f} / Target: ${target_profit:,.2f}. "
                    f"Consider completing session or trading Ultra Safe (Level 1)."
                )
            elif max_planned_trades is not None:
                rem_profit = target_profit - current_pnl
                rem_trades = max_planned_trades - trades_count

                if rem_trades <= 0:
                    target_status_note = (
                        f"⚠️  MAX PLANNED TRADES REACHED ({trades_count}/{max_planned_trades})! "
                        f"Target Profit: ${target_profit:,.2f} (P&L: ${current_pnl:+,.2f})."
                    )
                else:
                    needed_profit_per_trade = rem_profit / rem_trades
                    payout_factor = (payout_pct / 100.0) if payout_pct > 0 else 1.0
                    target_optimal_stake = round(needed_profit_per_trade / payout_factor, 2)
                    target_status_note = (
                        f"🎯  SESSION GOAL: Needs +${needed_profit_per_trade:,.2f}/trade over "
                        f"{rem_trades} remaining willing trade(s) to hit ${target_profit:,.2f} target."
                    )

        # Calculate streak & performance context
        trades = TradeModel.all(account_id, session_id=session_id)
        recent_closed = [t for t in trades if t["status"] == "CLOSED"][:5]

        consecutive_losses = 0
        consecutive_wins   = 0
        for t in recent_closed:
            pnl = float(t["pnl"] or 0)
            if pnl < 0:
                if consecutive_wins == 0:
                    consecutive_losses += 1
                else:
                    break
            elif pnl > 0:
                if consecutive_losses == 0:
                    consecutive_wins += 1
                else:
                    break

        recommendation_note = None
        recommended_level   = 2  # default Conservative

        if consecutive_losses >= 2:
            recommendation_note = (
                f"⚠️  Loss streak detected ({consecutive_losses} Ls). "
                f"Smart Engine recommends Level 1 (Ultra Safe) to preserve capital!"
            )
            recommended_level = 1
        elif consecutive_wins >= 3:
            recommendation_note = (
                f"🔥  Win streak detected ({consecutive_wins} Ws)! "
                f"Level 2 or 3 recommended for disciplined growth."
            )

        # Build 5 safety levels
        calculated_levels = []
        for item in cls.SAFETY_LEVELS:
            lvl_pct = item["pct"]

            if item["level"] == 5 and max_risk_pct > 0:
                lvl_pct = min(lvl_pct, max_risk_pct)

            stake_amount = round(base_capital * (lvl_pct / 100.0), 2)
            stake_amount = max(stake_amount, 1.0)

            payout_profit = round(stake_amount * (payout_pct / 100.0), 2)
            total_payout  = round(stake_amount + payout_profit, 2)

            is_recommended = (item["level"] == recommended_level)
            is_breach      = (lvl_pct > max_risk_pct)

            calculated_levels.append(
                {
                    "level": item["level"],
                    "name": item["name"],
                    "pct": lvl_pct,
                    "badge": item["badge"],
                    "tag": item["tag"],
                    "desc": item["desc"],
                    "stake_amount": stake_amount,
                    "payout_profit": payout_profit,
                    "total_payout": total_payout,
                    "is_recommended": is_recommended,
                    "is_breach": is_breach,
                }
            )

        return {
            "base_capital": base_capital,
            "capital_source": capital_source,
            "max_risk_pct": max_risk_pct,
            "max_pos_pct": max_pos_pct,
            "target_profit": target_profit,
            "max_planned_trades": max_planned_trades,
            "target_status_note": target_status_note,
            "target_optimal_stake": target_optimal_stake,
            "recommendation_note": recommendation_note,
            "recommended_level": recommended_level,
            "levels": calculated_levels,
        }
