#!/bin/bash
# Start Django preprocessing service on local network

cd "$(dirname "$0")"

# Get local IP address
LOCAL_IP=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d/ -f1 | head -1)

echo "========================================="
echo "Starting Django Preprocessing Service"
echo "========================================="
echo ""
echo "Local Network Access:"
echo "  → http://$LOCAL_IP:8001"
echo "  → http://localhost:8001"
echo ""
echo "Share this URL with devices on your network:"
echo "  http://$LOCAL_IP:8001"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

# Activate virtual environment and start server
source venv/bin/activate
python manage.py runserver 0.0.0.0:8001
