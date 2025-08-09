@echo off
echo Starting Kisan-G Application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed or not in PATH. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo npm is not installed or not in PATH. Please install npm first.
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Installing Node.js dependencies...
npm install

echo.
echo Starting servers...
echo Backend server will start on http://localhost:5001
echo Frontend server will start on http://localhost:3000
echo.

REM Start both servers in parallel
start cmd /k "cd /d %~dp0\server && python app.py"
timeout /t 3
start cmd /k "cd /d %~dp0 && npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5001
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
