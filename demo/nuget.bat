@echo off
setlocal
cd /d "%~dp0.."
if not exist output mkdir output
python "%~dp0..\run.py" --demo "%~dp0nuget.txt"
pause
