@echo off
REM Premier League Predictor Startup Script for Windows
REM This script sets up and starts both backend and frontend

echo 🚀 Starting Premier League Predictor...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

REM Activate virtual environment and install dependencies
echo 📦 Installing Python dependencies...
cd backend
call venv\Scripts\activate
pip install -r ..\requirements.txt
cd ..

REM Install frontend dependencies
echo 📦 Installing Node.js dependencies...
cd frontend
if not exist "node_modules" (
    npm install
)
cd ..

echo ✅ Dependencies installed successfully!

REM Start backend in background
echo 🔧 Starting backend server...
cd backend
call venv\Scripts\activate
start "Backend Server" cmd /k "python main.py"
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🎨 Starting frontend server...
cd frontend
start "Frontend Server" cmd /k "npm start"
cd ..

echo.
echo 🎉 Premier League Predictor is starting up!
echo.
echo 📊 Backend API: http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo 🎨 Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
