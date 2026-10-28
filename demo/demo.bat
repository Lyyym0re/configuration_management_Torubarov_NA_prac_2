@echo off
setlocal
cd /d "%~dp0.."
python "%~dp0..\run.py" --demo "%~dp0commands.txt"
pause
