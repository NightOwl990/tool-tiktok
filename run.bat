@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating local virtual environment...
    python -m venv .venv
    if errorlevel 1 goto error
)

echo Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo Importing Reddit CSV...
".venv\Scripts\python.exe" import_reddit_csv.py
if errorlevel 1 goto error

echo Importing TikTok CSV...
".venv\Scripts\python.exe" import_tiktok_csv.py
if errorlevel 1 goto error

echo Importing TikTok analytics CSV...
".venv\Scripts\python.exe" import_tiktok_analytics_csv.py
if errorlevel 1 goto error

echo Scoring trends...
".venv\Scripts\python.exe" score_trends.py
if errorlevel 1 goto error

echo Starting dashboard...
".venv\Scripts\python.exe" -m streamlit run dashboard.py
goto end

:error
echo.
echo Run failed. Check the message above.
pause
exit /b 1

:end
endlocal
