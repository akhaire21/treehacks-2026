#!/bin/bash
# Stop Backend Server

echo "🛑 Stopping backend server on port 5001..."

PID=$(lsof -ti:5001)
if [ ! -z "$PID" ]; then
    kill -9 $PID
    echo "✅ Backend stopped (killed PID: $PID)"
else
    echo "ℹ️  No backend process found on port 5001"
fi
