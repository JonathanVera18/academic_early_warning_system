# 🚀 Free Cloud Deployment Guide

## Overview
Deploy your Academic Early Warning System for **FREE** using:
- **Frontend**: Vercel (React app)
- **Backend**: Render (Flask API)
- **Database**: Supabase (already configured)

**Total Monthly Cost: $0** (with free tiers)

---

## 📋 Prerequisites
- GitHub account (you have: https://github.com/samuelcampozano/Academic-Early-Warning-System)
- Vercel account (free): https://vercel.com
- Render account (free): https://render.com

---

## Step 1: Deploy Backend on Render (Flask API)

### 1.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended for easy repo access)

### 1.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `samuelcampozano/Academic-Early-Warning-System`
3. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `academic-early-warning-api` |
| **Region** | Oregon (US West) |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| **Plan** | **Free** |

### 1.3 Add Environment Variables
In Render dashboard, go to **Environment** and add:

```
FLASK_ENV=production
SUPABASE_URL=https://tuvwchddzwallvvwwaor.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1dndjaGRkendhbGx2dnd3YW9yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwODAzMTksImV4cCI6MjA3ODY1NjMxOX0.H3y3PFDXckp3nfGZgPLNWnxNusINh8-qh0d09S4Z3ok
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1dndjaGRkendhbGx2dnd3YW9yIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzA4MDMxOSwiZXhwIjoyMDc4NjU2MzE5fQ.EzJjcdEYlqiHhHm3KLTPldqESo65iCPGDaNN9EQVIo8
FRONTEND_URL=https://your-app-name.vercel.app
SECRET_KEY=your-secure-random-key-here
LOG_LEVEL=INFO
```

### 1.4 Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes first time)
3. Your API will be at: `https://academic-early-warning-api.onrender.com`

> ⚠️ **Note**: Free tier sleeps after 15 min of inactivity. First request may take 30-60 seconds to wake up.

---

## Step 2: Deploy Frontend on Vercel (React App)

### 2.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

### 2.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Import from GitHub: `samuelcampozano/Academic-Early-Warning-System`
3. Configure:

| Setting | Value |
|---------|-------|
| **Project Name** | `academic-early-warning` |
| **Framework Preset** | Create React App |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `build` |

### 2.3 Add Environment Variables
Add this environment variable:

```
REACT_APP_API_URL=https://academic-early-warning-api.onrender.com/api
```

(Replace with your actual Render URL from Step 1)

### 2.4 Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Your app will be at: `https://academic-early-warning.vercel.app`

---

## Step 3: Update CORS (Final Step)

Go back to Render and update the `FRONTEND_URL` environment variable with your actual Vercel URL:

```
FRONTEND_URL=https://academic-early-warning.vercel.app
```

Then click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🎉 You're Done!

Your application is now live at:
- **Frontend**: https://academic-early-warning.vercel.app
- **Backend API**: https://academic-early-warning-api.onrender.com

---

## 📊 Free Tier Limits

### Render (Backend)
- 750 hours/month free (enough for 1 service 24/7)
- Sleeps after 15 min inactivity
- 512 MB RAM
- Shared CPU

### Vercel (Frontend)
- Unlimited deployments
- 100 GB bandwidth/month
- Automatic HTTPS
- Custom domains supported

### Supabase (Database)
- 500 MB database
- 2 GB bandwidth
- 50,000 monthly active users
- Unlimited API requests

---

## 🔧 Troubleshooting

### Backend not responding
1. Check Render logs in dashboard
2. Verify environment variables are set
3. Free tier may be sleeping - wait 30 seconds

### CORS errors
1. Verify FRONTEND_URL matches your Vercel URL exactly
2. Include `https://` in the URL
3. Redeploy backend after changing env vars

### Database connection issues
1. Verify SUPABASE_URL and keys are correct
2. Check Supabase dashboard for any RLS issues

---

## 🔄 Continuous Deployment

Both Vercel and Render auto-deploy when you push to GitHub:
1. Make changes locally
2. `git add .`
3. `git commit -m "your message"`
4. `git push`
5. Both services automatically rebuild and deploy!

---

## 📱 Custom Domain (Optional)

### Vercel (Free)
1. Go to Project Settings → Domains
2. Add your domain (e.g., `alertas.juanmontalvo.edu.ec`)
3. Update DNS records as instructed

### Render (Free)
1. Go to Service Settings → Custom Domains
2. Add your API domain (e.g., `api.juanmontalvo.edu.ec`)
3. Update DNS records
