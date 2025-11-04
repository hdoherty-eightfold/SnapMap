# SnapMap Deployment Guide

This guide covers multiple deployment options for SnapMap.

## 🚀 Quick Deploy Options

### Option 1: Render (Recommended - Free Tier Available)

**Render** is perfect for full-stack apps. Both frontend and backend in one place.

#### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/SnapMap.git
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repo
   - Render will auto-detect `render.yaml` and deploy both services!

3. **Done!**
   - Backend: `https://snapmap-backend.onrender.com`
   - Frontend: `https://snapmap-frontend.onrender.com`

**Pros:**
- ✅ Free tier (750 hours/month)
- ✅ Auto-deploys on git push
- ✅ Built-in SSL
- ✅ Persistent disk storage for vector DB

**Cons:**
- ⚠️ Free tier spins down after inactivity (30 sec startup)

---

### Option 2: Railway (Easy, $5/month)

**Railway** is developer-friendly with great DX.

#### Steps:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Done!**

**Pros:**
- ✅ $5 free credit per month
- ✅ Always-on (no cold starts)
- ✅ Easy environment variables
- ✅ Fast deployments

**Cons:**
- ⚠️ Costs money after free tier ($5-20/month)

---

### Option 3: Docker (Self-Hosted)

Deploy anywhere that supports Docker.

#### Steps:

1. **Build and run**
   ```bash
   docker-compose up -d
   ```

2. **Access**
   - App: `http://localhost:8000`

**Pros:**
- ✅ Run anywhere (VPS, cloud, local)
- ✅ Complete control
- ✅ Easy to update

**Cons:**
- ⚠️ Need to manage server
- ⚠️ Need to setup SSL manually

---

### Option 4: Vercel (Frontend) + Render (Backend)

Split deployment for optimal performance.

#### Frontend to Vercel:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy frontend**
   ```bash
   cd frontend
   vercel
   ```

#### Backend to Render:

Follow "Option 1" but only deploy backend service.

**Pros:**
- ✅ Best performance (Vercel CDN)
- ✅ Free frontend hosting
- ✅ Automatic HTTPS

**Cons:**
- ⚠️ Two separate services to manage

---

## 🔧 Configuration

### Environment Variables

Create `.env` files for each environment:

**Backend (`backend/.env`):**
```env
ENVIRONMENT=production
LOG_LEVEL=info
CORS_ORIGINS=https://your-frontend.vercel.app
```

**Frontend (`frontend/.env.production`):**
```env
VITE_API_URL=https://snapmap-backend.onrender.com/api
```

---

## 📦 Vector Database Setup

The vector database needs to be built on first deployment:

### Automatic (Recommended)
The `render.yaml` and `Dockerfile` automatically run `python build_vector_db.py` during deployment.

### Manual
If you need to rebuild:

```bash
# SSH into your deployment
python build_vector_db.py --rebuild
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Set `ENVIRONMENT=production` in env vars
- [ ] Configure `CORS_ORIGINS` to your frontend URL
- [ ] Add rate limiting (not included, use nginx or Cloudflare)
- [ ] Enable HTTPS (automatic on Render/Vercel)
- [ ] Set up monitoring (use Render's built-in or Sentry)
- [ ] Configure backup for vector database
- [ ] Review uploaded file size limits

---

## 📊 Monitoring

### Render Dashboard
- View logs in real-time
- Monitor CPU/memory usage
- Set up alerts

### Health Check
All deployments include a health endpoint:
```bash
curl https://your-backend.onrender.com/health
```

Response:
```json
{"status": "healthy"}
```

---

## 🔄 Updates

### Auto-Deploy (Render/Railway)
Just push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push
```

Render automatically deploys!

### Docker
```bash
docker-compose pull
docker-compose up -d
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Render** | 750 hrs/mo | $7/mo | Full-stack apps |
| **Railway** | $5 credit | $5-20/mo | Always-on apps |
| **Vercel** | Unlimited | $20/mo | Frontend only |
| **Docker (VPS)** | N/A | $5-10/mo | Full control |
| **Heroku** | No free tier | $7/mo | Legacy apps |

---

## 🐛 Troubleshooting

### Vector DB not found
```bash
# Rebuild the database
python build_vector_db.py
```

### ChromaDB errors
```bash
# Clear and rebuild
rm -rf vector_db/*
python build_vector_db.py --rebuild
```

### Frontend can't reach backend
Check `VITE_API_URL` in frontend environment variables.

### Slow cold starts (Render free tier)
Upgrade to paid tier ($7/mo) for always-on service.

---

## 🎯 Recommended Setup for Production

**Best Performance + Cost:**
- **Frontend**: Vercel (free, CDN)
- **Backend**: Render Starter ($7/mo, always-on)
- **Monitoring**: Sentry (free tier)
- **Domain**: Namecheap ($10/year)

**Total Cost**: ~$17/month for production-ready setup

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [ChromaDB Docs](https://docs.trychroma.com)

---

## 🚦 GitHub Actions (CI/CD)

The project includes `.github/workflows/deploy.yml` for automated:
- ✅ Testing on every push
- ✅ Building Docker images
- ✅ Auto-deployment to Render

Just push to `main` branch and everything deploys automatically!
