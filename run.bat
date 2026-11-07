@echo off
setlocal

rem Launcher for the legacy tkinter GUI.
rem Picks a project virtualenv if present, otherwise falls back to PATH python.

set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"

rem Auto-detect the Tcl library bundled with this interpreter. Without this,
rem some Python installs fail with "Can't find a usable init.tcl".
rem (Kept out of an if-block: parentheses in the command would break cmd parsing.)
if defined TCL_LIBRARY goto :after_tcl
set "TCLTMP=%TEMP%\yowes_tcl.tmp"
"%PYTHON%" -c "import os,sys;d=os.path.join(sys.base_prefix,'tcl','tcl8.6');print(d if os.path.isdir(d) else '')" > "%TCLTMP%" 2>nul
set /p TCL_LIBRARY=<"%TCLTMP%"
del "%TCLTMP%" >nul 2>nul
:after_tcl

"%PYTHON%" "%~dp0main_gui.py" %*

endlocal
