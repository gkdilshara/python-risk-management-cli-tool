# ============================================================
#  main.py — Application Entrypoint
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.init_db     import init_database
from db.connection  import DBConnection
from ui.helpers     import arrow_menu, clear, print_logo, section_header, pause, warning, info, error
from ui.theme       import C_DIM, C_RESET, C_BORDER, C_TITLE, C_HEADER
from ui.screens.dashboard   import screen_dashboard
from ui.screens.accounts    import screen_accounts
from ui.screens.trades      import screen_trades
from ui.screens.risk        import screen_risk
from ui.screens.journal     import screen_journal
from ui.screens.calculator  import screen_calculator


MAIN_MENU = [
    "📊  Dashboard & Stats",
    "👤  Account Management",
    "📈  Trade Management",
    "🛡️   Risk Rules",
    "📓  Trading Journal",
    "🧮  Risk Calculator",
    "🚪  Exit",
]


def main():
    # ── Auto-create database & tables if they don't exist ────
    init_database()

    while True:
        choice = arrow_menu("MAIN MENU", MAIN_MENU)

        if choice == 0:   screen_dashboard()
        elif choice == 1: screen_accounts()
        elif choice == 2: screen_trades()
        elif choice == 3: screen_risk()
        elif choice == 4: screen_journal()
        elif choice == 5: screen_calculator()
        elif choice in (6, -1):
            clear()
            print_logo()
            section_header("GOODBYE")
            print(f"\n  {C_HEADER}Thank you for using Risk Management System!{C_RESET}")
            print(f"  {C_DIM}Trade safe. Protect your capital.{C_RESET}\n")
            DBConnection.close()
            sys.exit(0)


if __name__ == "__main__":
    main()
