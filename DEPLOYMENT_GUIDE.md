# 🚀 SKILLTRACE: Cloud Deployment Guide

This guide walks you through deploying **SKILLTRACE** live on the web as a production website with automatic HTTPS, custom domain support, and free 24/7 cloud hosting.

---

## 🌟 Recommended Platform: Render.com (100% Free & Simplest)

[Render](https://render.com) provides free web service hosting for Python/FastAPI web apps with built-in HTTPS and zero server configuration.

### Step 1: Push Your Code to GitHub
1. Open your terminal in this project folder (`C:\Users\Lohitha16\Desktop\SIH`).
2. Create a new repository on [GitHub](https://github.com/new) (e.g. `skilltrace-sih-2026`).
3. Push your code:
   ```bash
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/skilltrace-sih-2026.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render in 1 Click
1. Go to [dashboard.render.com](https://dashboard.render.com) and sign up/sign in with your GitHub account.
2. Click the blue **"New +"** button at the top and select **"Web Service"**.
3. Select your repository: `skilltrace-sih-2026`.
4. Fill in the deployment settings:
   - **Name**: `skilltrace` (or your preferred name)
   - **Region**: Closest to you (e.g., *Singapore* or *Frankfurt*)
   - **Branch**: `main`
   - **Root Directory**: *(Leave blank)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free**
5. Click **"Create Web Service"**!

Render will automatically build and deploy your application. In ~2 minutes, your site will be live at:
```
https://skilltrace.onrender.com
```

---

## ⚡ Alternative 1: Railway.app (Instant 1-Click)

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **"New Project"** &rarr; **"Deploy from GitHub repo"**.
3. Select your `skilltrace-sih-2026` repository.
4. Railway will automatically detect the included `Procfile` / `Dockerfile` and deploy the app.
5. In your project settings, click **"Generate Domain"** to get your live public URL!

---

## 🐳 Alternative 2: Docker Container (Deploy Anywhere)

Because this repository includes a production [`Dockerfile`](Dockerfile) and [`.dockerignore`](.dockerignore), you can also run it in Docker:

```bash
# Build the Docker image
docker build -t skilltrace:latest .

# Run the container locally on port 8000
docker run -p 8000:8000 skilltrace:latest
```

This container can be pushed directly to **Google Cloud Run**, **AWS ECS/App Runner**, **Azure Container Apps**, or **DigitalOcean**.

---

## ⚙️ Environment Variables (Optional)

When deploying, you can optionally configure these environment variables in your hosting provider's dashboard:

| Variable | Default Value | Description |
|---|---|---|
| `PORT` | `8000` | Auto-assigned by cloud host |
| `DEBUG` | `false` | Disable debug logs in production |
| `ADMIN_USERNAME` | `admin` | Custom administrator username |
| `ADMIN_PASSWORD` | `admin123` | Custom administrator password |
| `DATABASE_URL` | `sqlite:///./skilltrace.db` | Switch to PostgreSQL if desired |

---

## 🌐 Live Pages Available on Your Deployed Site:
- **Landing Page**: `https://<your-app>.onrender.com/`
- **Role & Skill Directory**: `https://<your-app>.onrender.com/jobs.html`
- **Personalized Pre-Assessment**: `https://<your-app>.onrender.com/assessment.html`
- **Skill Profile Matcher**: `https://<your-app>.onrender.com/dashboard.html`
- **Administrator Portal**: `https://<your-app>.onrender.com/admin.html`
- **Interactive OpenAPI Documentation**: `https://<your-app>.onrender.com/docs`
