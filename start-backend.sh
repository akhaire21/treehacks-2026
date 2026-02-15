#!/bin/bash
# Start Backend Server - Auto-kills old processes

echo "🔍 Checking port 5001..."

# Kill any process using port 5001
PID=$(lsof -ti:5001)
if [ ! -z "$PID" ]; then
    echo "⚠️  Found old process on port 5001 (PID: $PID)"
    kill -9 $PID 2>/dev/null
    echo "✅ Killed old process"
    sleep 1
fi

echo "✅ Port 5001 is free"
echo ""
echo "🚀 Starting Flask backend server..."
echo "📍 Location: $(pwd)/backend"
echo ""

cd "$(dirname "$0")/backend"
python api.py
