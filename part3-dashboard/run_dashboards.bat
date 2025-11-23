@echo off
REM Script to run the health risk dashboards on Windows

echo Health Risk Dashboard Launcher
echo ==============================
echo.
echo Select which dashboard to run:
echo 1. Authorities Dashboard (Health Authorities)
echo 2. Citizens Dashboard (Personal Health)
echo 3. Exit
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting Authorities Dashboard...
    streamlit run dashboard/authorities_app.py --server.port 8501
) else if "%choice%"=="2" (
    echo Starting Citizens Dashboard...
    streamlit run dashboard/citizens_app.py --server.port 8501
) else if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    exit /b 1
)

