# 🚀 Starting Your Servers

Quick guide to run both frontend and backend.

---

## Option 1: Using Terminal (Recommended for Development)

### Terminal 1: Backend (Flask)
```bash
cd backend
python api.py
```

**Expected output:**
```
============================================================
  Agent Workflow Marketplace API
============================================================
  Workflows loaded : 8
  Elasticsearch    : off (in-memory fallback)
  Claude Agent     : ready
  Orchestrator     : ready
  Visa payments    : disabled (no API key)
  JINA Embeddings  : off
  Commerce Engine  : active
  Server           : http://localhost:5001
============================================================
```

### Terminal 2: Frontend (Next.js)
```bash
npm run dev
```

**Expected output:**
```
  ▲ Next.js 14.2.0
  - Local:        http://localhost:3000
  - Ready in 2.1s
```

---

## Option 2: Using VS Code Terminal Split

1. Open integrated terminal in VS Code (`Ctrl + ~` or `Cmd + ~`)
2. Click the **split terminal** button (or `Cmd + \`)
3. In **left terminal**: `cd backend && python api.py`
4. In **right terminal**: `npm run dev`

---

## Option 3: Background Script (Quick Start)

Create this script: `start-dev.sh`
```bash
#!/bin/bash

# Start backend in background
cd backend
python api.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend..."
sleep 3

# Start frontend
echo "🚀 Starting frontend..."
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
```

Make it executable:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

---

## 🔍 Troubleshooting

### Backend won't start

**Error: "Port 5001 already in use"**
```bash
# Find what's using the port
lsof -i :5001

# Kill it
kill -9 <PID>

# Or use a different port in backend/.env:
FLASK_PORT=5002
```

**Error: "No module named 'flask'"**
```bash
cd backend
pip install -r requirements.txt
```

**Error: "No such file: api.py"**
```bash
# Make sure you're in the right directory
pwd
# Should show: .../treehacks-2026

cd backend
ls api.py  # Should exist
```

### Frontend won't start

**Error: "Module not found"**
```bash
npm install
```

**Error: "Port 3000 already in use"**
```bash
# Kill what's using port 3000
lsof -i :3000
kill -9 <PID>

# Or use a different port
PORT=3001 npm run dev
```

### Marketplace shows "Failed to fetch"

1. ✅ Check backend is running: `http://localhost:5001/health`
2. ✅ Check CORS is enabled (already configured in `api.py`)
3. ✅ Check `.env.local` has: `NEXT_PUBLIC_API_URL=http://localhost:5001`
4. ✅ Restart frontend after changing env vars

---

## 🧪 Test Everything is Working

### 1. Backend Health Check
```bash
curl http://localhost:5001/health
```

**Expected:**
```json
{
  "status": "healthy",
  "workflows_loaded": 8,
  "elasticsearch": false,
  "agent_enabled": true,
  "orchestrator_enabled": true,
  "visa_payments_enabled": false
}
```

### 2. Get Workflows
```bash
curl http://localhost:5001/api/workflows
```

**Expected:**
```json
{
  "workflows": [...],
  "count": 8
}
```

### 3. Frontend
Visit: http://localhost:3000/marketplace

Should show 8 workflows with pricing!

---

## ✅ Quick Checklist

Before you start:
- [ ] Backend `.env` file exists with API keys
- [ ] Frontend `.env.local` exists with Supabase credentials
- [ ] Dependencies installed: `pip install -r backend/requirements.txt`
- [ ] Dependencies installed: `npm install`
- [ ] Both servers running (backend on 5001, frontend on 3000)

---

## 🎯 Development Workflow

**Normal workflow:**
1. Start backend: `cd backend && python api.py`
2. Start frontend (new terminal): `npm run dev`
3. Code and refresh browser
4. Stop with `Ctrl+C` in each terminal

**Backend changes:**
- Stop backend (`Ctrl+C`)
- Make changes
- Restart: `python api.py`

**Frontend changes:**
- Changes auto-reload (Hot Module Replacement)
- No restart needed
- If broken, restart with `npm run dev`

**Environment variable changes:**
- Backend: Restart Flask server
- Frontend: Restart Next.js dev server

---

**Happy coding! 🚀**
