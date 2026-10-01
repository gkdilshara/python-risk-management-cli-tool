@echo off
chcp 65001 >nul
title Risk Management System — by Sasindu Dilshara
color 0B

echo.
echo   ██████╗ ██╗███████╗██╗  ██╗    ███╗   ███╗ ██████╗ ███╗   ███╗████████╗
echo   ██╔══██╗██║██╔════╝██║ ██╔╝    ████╗ ████║██╔════╝ ████╗ ████║╚══██╔══╝
echo   ██████╔╝██║███████╗█████╔╝     ██╔████╔██║██║  ███╗██╔████╔██║   ██║
echo   ██╔══██╗██║╚════██║██╔═██╗     ██║╚██╔╝██║██║   ██║██║╚██╔╝██║   ██║
echo   ██║  ██║██║███████║██║  ██╗    ██║ ╚═╝ ██║╚██████╔╝██║ ╚═╝ ██║   ██║
echo   ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝     ╚═╝ ╚═════╝ ╚═╝     ╚═╝   ╚═╝
echo.
echo   ┌─────────────────────────────────────────────────────────────────────┐
echo   │        T R A D I N G   R I S K   M A N A G E M E N T   C L I       │
echo   │                      --- by Sasindu Dilshara ---                    │
echo   └─────────────────────────────────────────────────────────────────────┘
echo.
echo   Starting application...
echo.

:: Activate virtual environment
call "%~dp0.venv\Scripts\activate.bat"

:: Launch the app
python "%~dp0main.py"

:: On exit
echo.
echo   Application closed.
pause
