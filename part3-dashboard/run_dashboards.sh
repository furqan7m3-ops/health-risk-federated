#!/bin/bash

# Script to run the health risk dashboards

echo "Health Risk Dashboard Launcher"
echo "=============================="
echo ""
echo "Select which dashboard to run:"
echo "1. Authorities Dashboard (Health Authorities)"
echo "2. Citizens Dashboard (Personal Health)"
echo "3. Exit"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Starting Authorities Dashboard..."
        streamlit run dashboard/authorities_app.py --server.port 8501
        ;;
    2)
        echo "Starting Citizens Dashboard..."
        streamlit run dashboard/citizens_app.py --server.port 8501
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

