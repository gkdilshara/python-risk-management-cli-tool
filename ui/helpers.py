# ============================================================
#  ui/helpers.py — Shared UI utilities
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

import os
import sys
import msvcrt
from ui.theme import *


# ── Terminal helpers ─────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg="  Press any key to continue..."):
    print(f"\n{C_DIM}{msg}{C_RESET}")
    msvcrt.getch()


def print_logo():
    clear()
    print(C_TITLE + LOGO)
    print(C_BORDER + LOGO_SUBTITLE)
    print(C_BORDER + LOGO_LINE)
    print(C_DIM   + LOGO_AUTHOR)
    print(C_BORDER + LOGO_BOTTOM)
    print()


def section_header(title: str):
    width = 72
    bar   = "=" * width
    pad   = (width - len(title) - 2) // 2
    print(C_BORDER + f"  +{bar}+")
    print(C_BORDER + f"  |{' ' * pad} " + C_HEADER + title + C_BORDER + f" {' ' * (width - pad - len(title) - 1)}|")
    print(C_BORDER + f"  +{bar}+")
    print()


def info(msg):    print(C_SUCCESS + f"  [OK]  {msg}" + C_RESET)
def error(msg):   print(C_ERROR   + f"  [!!]  {msg}" + C_RESET)
def warning(msg): print(C_WARN    + f"  [**]  {msg}" + C_RESET)


def prompt(label: str, default=None) -> str:
    hint = f" [{default}]" if default is not None else ""
    val  = input(f"  {C_HEADER}{label}{hint}: {C_RESET}").strip()
    if val == "" and default is not None:
        return str(default)
    return val


def prompt_float(label: str, default=None) -> float:
    while True:
        raw = prompt(label, default)
        try:
            return float(raw)
        except ValueError:
            error("Please enter a valid number.")


def prompt_int(label: str, default=None) -> int:
    while True:
        raw = prompt(label, default)
        try:
            return int(raw)
        except ValueError:
            error("Please enter a valid integer.")


def prompt_choice(label: str, choices: list) -> str:
    while True:
        raw = prompt(label).upper()
        if raw in [c.upper() for c in choices]:
            return raw
        error(f"Invalid choice. Must be one of: {', '.join(choices)}")


# ── Arrow-key menu (flicker-free) ────────────────────────────

def arrow_menu(title: str, items: list, subtitle: str = "") -> int:
    """
    Display a navigable menu using arrow keys (UP/DOWN).
    Returns the 0-based index of the selected item, or -1 if ESC pressed.

    Anti-flicker strategy
    ─────────────────────
    Logo + header are drawn ONCE on first render.
    On every subsequent keypress, only the menu rows are rewritten
    in-place using ANSI cursor-up + line-clear escape codes.
    No full 'cls' is ever called again — zero screen flicker.
    """
    selected   = 0
    total      = len(items)
    first_draw = True

    # Total lines in the managed (re-drawn) region:
    #   subtitle line + blank  (if subtitle present)
    #   + one line per item
    #   + blank line
    #   + nav-hint line
    sub_lines  = 2 if subtitle else 0
    menu_lines = sub_lines + total + 2

    def _render():
        """Write/overwrite only the managed menu region."""
        lines = []

        if subtitle:
            lines.append(f"  {C_DIM}{subtitle}{C_RESET}")
            lines.append("")

        for i, item in enumerate(items):
            if i == selected:
                lines.append(f"  {C_SELECT}[ ▶  {item} ]{C_RESET}")
            else:
                lines.append(f"  {C_MENU}     {item}  {C_RESET}")

        lines.append("")
        lines.append(f"  {C_DIM}[UP/DOWN] Navigate   [Enter] Select   [Esc] Back{C_RESET}")

        for line in lines:
            sys.stdout.write(f"\r\033[2K{line}\n")
        sys.stdout.flush()

    while True:
        if first_draw:
            clear()
            print_logo()
            section_header(title)
            _render()
            first_draw = False
        else:
            # Move cursor back up to the start of the managed region,
            # then overwrite — logo/header are never touched again.
            sys.stdout.write(f"\033[{menu_lines}A")
            _render()

        key = _read_key()

        if key == "UP":
            selected = (selected - 1) % total
        elif key == "DOWN":
            selected = (selected + 1) % total
        elif key == "ENTER":
            return selected
        elif key == "ESC":
            return -1


def _read_key() -> str:
    """Read a single key press and return a label string."""
    ch = msvcrt.getch()

    if ch in (b"\r", b"\n"):
        return "ENTER"
    if ch == b"\x1b":
        return "ESC"
    if ch in (b"\x00", b"\xe0"):        # extended key prefix on Windows
        ch2 = msvcrt.getch()
        if ch2 == b"H":   return "UP"
        if ch2 == b"P":   return "DOWN"
        if ch2 == b"K":   return "LEFT"
        if ch2 == b"M":   return "RIGHT"
        if ch2 == b"S":   return "DELETE"
    return ch.decode("utf-8", errors="ignore")
