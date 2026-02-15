# Quick Start: Render + Vercel Deployment

This is the fastest way to get your app deployed!

## 🚀 Deploy in 5 Minutes

### 1. Deploy Backend to Render (2 minutes)

1. **Go to Render**: https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn api:app`
5. Add these environment variables:
   ```
   ANTHROPIC_API_KEY=sk-...
   JINA_API_KEY=jina_...
   ELASTIC_CLOUD_ID=...
   ELASTIC_API_KEY=...
   FLASK_ENV=production
   FLASK_DEBUG=false
   ```
6. Click **"Create Web Service"**
7. **Copy your backend URL** (e.g., `https://treehacks-backend.onrender.com`)

### 2. Deploy Frontend to Vercel (2 minutes)

1. **Update [vercel.json](vercel.json)** with your Render URL:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://YOUR-BACKEND-URL.onrender.com/api/:path*"
       }
     ]
   }
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update backend URL"
   git push
   ```

3. **Go to Vercel**: https://vercel.com/new
4. Import your GitHub repo
5. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-URL.onrender.com
   ```
6. Click **"Deploy"**

### 3. Test (1 minute)

```bash
# Test backend
curl https://your-backend.onrender.com/health

# Visit frontend
open https://your-frontend.vercel.app
```

## 📋 Checklist

Backend (Render):
- [ ] Service created
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Health check passes

Frontend (Vercel):
- [ ] vercel.json updated with backend URL
- [ ] Environment variable set
- [ ] Deployment successful
- [ ] Can access app in browser

## 🔑 Required API Keys

Get these before deploying:

1. **Anthropic**: https://console.anthropic.com/
2. **JINA**: https://jina.ai/
3. **Elasticsearch**: https://cloud.elastic.co/

## ⚡ Common Issues

**Backend won't start?**
- Check environment variables are set
- View logs in Render dashboard
- Ensure all API keys are valid

**Frontend can't reach backend?**
- Verify backend URL in vercel.json
- Check NEXT_PUBLIC_API_URL is set
- Ensure backend is deployed and healthy

**CORS errors?**
- Backend has CORS enabled by default
- Check the backend URL is correct

## 📚 Full Documentation

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **This Repo**: Create an issue on GitHub
