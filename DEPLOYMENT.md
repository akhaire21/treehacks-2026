# Deployment Guide

This guide will help you deploy the TreeHacks 2026 project with a Flask backend on Render and a Next.js frontend on Vercel.

## Architecture

- **Backend**: Flask API hosted on Render
- **Frontend**: Next.js app hosted on Vercel
- **Services**: Elasticsearch Cloud, JINA Embeddings, Anthropic Claude

## Prerequisites

1. A [Render](https://render.com) account
2. A [Vercel](https://vercel.com) account
3. API keys for:
   - Anthropic (Claude)
   - JINA Embeddings
   - Elasticsearch Cloud

---

## Part 1: Deploy Backend to Render

### Step 1: Push your code to GitHub

Make sure your latest code is pushed to a GitHub repository.

```bash
git add .
git commit -m "Add deployment configurations"
git push origin main
```

### Step 2: Create a new Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `treehacks-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api:app`
   - **Plan**: Free (or your preferred plan)

### Step 3: Set Environment Variables on Render

In your Render service settings, go to **Environment** and add these variables:

**Required:**
```
ANTHROPIC_API_KEY=your-anthropic-api-key-here
JINA_API_KEY=your-jina-api-key-here
ELASTIC_CLOUD_ID=your-elastic-cloud-id-here
ELASTIC_API_KEY=your-elastic-api-key-here
```

**Optional (with defaults):**
```
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_MAX_TOKENS=4096
JINA_MODEL=jina-embeddings-v3
JINA_EMBEDDING_DIM=1024
ELASTIC_INDEX=workflows
FLASK_PORT=5001
FLASK_DEBUG=false
FLASK_ENV=production
SCORE_THRESHOLD_GOOD=0.85
SCORE_IMPROVEMENT_EPSILON=0.1
MAX_RECURSION_DEPTH=2
SUBTASKS_MIN=2
SUBTASKS_MAX=8
```

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically deploy your backend
3. Once deployed, note your backend URL (e.g., `https://treehacks-backend.onrender.com`)

### Step 5: Test your Backend

```bash
curl https://your-backend-name.onrender.com/health
```

You should see a JSON response with `"status": "healthy"`.

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Update vercel.json

Open [vercel.json](vercel.json) and replace `your-backend-name` with your actual Render service name:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@backend_url"
  },
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-ACTUAL-BACKEND-NAME.onrender.com/api/:path*"
    }
  ]
}
```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

```bash
# Install Vercel CLI if you haven't
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

#### Option B: Using Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `./` (project root)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Set Environment Variables on Vercel

In your Vercel project settings:

1. Go to **Settings** → **Environment Variables**
2. Add the following:

```
NEXT_PUBLIC_API_URL=https://your-backend-name.onrender.com
```

### Step 4: Redeploy

After adding environment variables, trigger a new deployment:

```bash
vercel --prod
```

Or redeploy from the Vercel dashboard.

---

## Part 3: Verify Deployment

### Test the Full Stack

1. **Backend Health Check**:
   ```bash
   curl https://your-backend-name.onrender.com/health
   ```

2. **Frontend**: Visit your Vercel URL (e.g., `https://your-project.vercel.app`)

3. **API Integration**: Check that the frontend can communicate with the backend

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy .env.example to .env and fill in your keys
cp .env.example .env

# Run the backend
python api.py
```

### Frontend

```bash
# Copy .env.local.example to .env.local
cp .env.local.example .env.local

# Edit .env.local to point to your local backend
# NEXT_PUBLIC_API_URL=http://localhost:5001

# Install dependencies
npm install

# Run the frontend
npm run dev
```

---

## Troubleshooting

### Backend Issues

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Port Issues**: Render automatically assigns ports, so don't hardcode ports in production
3. **Environment Variables**: Double-check all required API keys are set

### Frontend Issues

1. **API Connection**: Verify `NEXT_PUBLIC_API_URL` is correctly set
2. **CORS**: The backend has CORS enabled for all origins
3. **Build Errors**: Check Next.js version compatibility

### Common Errors

**"Module not found"**: Add missing package to `requirements.txt` or `package.json`

**"CORS Error"**: Ensure your backend is running and CORS is enabled (already configured in `api.py`)

**"API Key not found"**: Check environment variables on Render/Vercel

---

## Monitoring

### Render

- View logs in the Render dashboard under **Logs**
- Monitor metrics under **Metrics**

### Vercel

- View deployment logs in the Vercel dashboard
- Monitor function logs under **Functions**

---

## Updating Deployments

### Backend (Render)

Render automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update backend"
git push origin main
```

### Frontend (Vercel)

Vercel automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update frontend"
git push origin main
```

Or manually deploy:

```bash
vercel --prod
```

---

## Cost Optimization

### Free Tier Limits

- **Render**: 750 hours/month (free plan)
- **Vercel**: 100GB bandwidth, 100 serverless function executions (hobby plan)
- **Elasticsearch**: 14-day free trial, then paid
- **JINA**: Check their pricing
- **Anthropic**: Usage-based pricing

### Tips

1. Use free tiers for development/testing
2. Monitor API usage to avoid unexpected costs
3. Consider caching responses to reduce API calls
4. Use Render's sleep feature for infrequently accessed services

---

## Security Checklist

- [ ] Never commit `.env` files
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS (automatic on Render/Vercel)
- [ ] Regularly rotate API keys
- [ ] Monitor API usage for anomalies
- [ ] Keep dependencies updated

---

## Support

For issues:
- **Render**: [Render Docs](https://render.com/docs)
- **Vercel**: [Vercel Docs](https://vercel.com/docs)
- **Project Issues**: Create an issue in your GitHub repository
