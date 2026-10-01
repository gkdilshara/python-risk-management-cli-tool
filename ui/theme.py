# ============================================================
#  ui/theme.py — Colors & Styles
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

import sys
from colorama import Fore, Back, Style, init

# Initialize colorama (strip codes when not a TTY, keep them in terminal)
init(autoreset=True)

# ── Enable ANSI Virtual Terminal Processing on Windows ───────
# Required so that cursor-move (\033[nA) and line-clear (\033[2K)
# escape codes work properly in cmd.exe and older PowerShell.
if sys.platform == "win32":
    import ctypes
    try:
        kernel32 = ctypes.windll.kernel32
        # Get current stdout console mode
        handle = kernel32.GetStdHandle(-11)          # STD_OUTPUT_HANDLE
        mode   = ctypes.c_ulong()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except Exception:
        pass  # Gracefully ignore if running in an unsupported environment

# Palette
C_TITLE   = Fore.CYAN  + Style.BRIGHT
C_MENU    = Fore.WHITE
C_SELECT  = Fore.CYAN  + Style.BRIGHT
C_HEADER  = Fore.YELLOW + Style.BRIGHT
C_SUCCESS = Fore.GREEN  + Style.BRIGHT
C_ERROR   = Fore.RED    + Style.BRIGHT
C_WARN    = Fore.YELLOW
C_DIM     = Style.DIM   + Fore.WHITE
C_PROFIT  = Fore.GREEN  + Style.BRIGHT
C_LOSS    = Fore.RED    + Style.BRIGHT
C_NEUTRAL = Fore.WHITE
C_BORDER  = Fore.CYAN
C_RESET   = Style.RESET_ALL

LOGO = r"""
  ██████╗ ██╗███████╗██╗  ██╗    ███╗   ███╗ ██████╗ ███╗   ███╗████████╗
  ██╔══██╗██║██╔════╝██║ ██╔╝    ████╗ ████║██╔════╝ ████╗ ████║╚══██╔══╝
  ██████╔╝██║███████╗█████╔╝     ██╔████╔██║██║  ███╗██╔████╔██║   ██║   
  ██╔══██╗██║╚════██║██╔═██╗     ██║╚██╔╝██║██║   ██║██║╚██╔╝██║   ██║   
  ██║  ██║██║███████║██║  ██╗    ██║ ╚═╝ ██║╚██████╔╝██║ ╚═╝ ██║   ██║   
  ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝     ╚═╝ ╚═════╝ ╚═╝     ╚═╝   ╚═╝   
"""

LOGO_SUBTITLE = "  ┌─────────────────────────────────────────────────────────────────────┐"
LOGO_LINE     = "  │        T R A D I N G   R I S K   M A N A G E M E N T   C L I       │"
LOGO_AUTHOR   = "  │                      ─── by Sasindu Dilshara ───                    │"
LOGO_BOTTOM   = "  └─────────────────────────────────────────────────────────────────────┘"
