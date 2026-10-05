@echo off
setlocal
cd /d "%~dp0"
py run_analysis.py
if errorlevel 1 (
  echo.
  echo Analysis failed. Install the dependencies with:
  echo   py -m pip install -r requirements.txt
)
pause
