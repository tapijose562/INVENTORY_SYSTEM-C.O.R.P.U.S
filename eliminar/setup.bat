@echo off
REM Inventory Corpus v2 - Startup Script for Windows

echo ===================================
echo Inventory Corpus v2 - Start-up
echo ===================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.13+
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo OK: %%i
echo.

REM Check Node
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js 20+
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo OK: %%i
echo.

REM Backend Setup
echo Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt -q

echo OK: Backend ready
echo.

REM Frontend Setup
echo Setting up Frontend...
cd ..\frontend

if not exist "node_modules" (
    echo Installing npm packages...
    call npm install -q
)

echo OK: Frontend ready
echo.

REM Back to root
cd ..

echo ===================================
echo Setup Complete!
echo ===================================
echo.
echo To start the application:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm start
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4200
echo API Docs: http://localhost:8000/docs
echo.
pause
