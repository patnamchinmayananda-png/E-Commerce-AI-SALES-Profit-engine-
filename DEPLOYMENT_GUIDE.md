# 🚀 Quick Deployment Guide

This project is pre-configured and 100% deployment-ready for **GitHub Pages**, **Vercel**, or **Netlify**.

---

## Option 1: Deploy to GitHub & GitHub Pages (Recommended - 100% Free)

### Step 1: Push to your GitHub Repository
In your terminal, run:
```bash
# Add your GitHub repository remote URL (replace with your repo link):
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# Push the main branch:
git push -u origin main
```

### Step 2: Enable GitHub Pages
1. On GitHub, go to your repository **Settings > Pages**.
2. Under **Build and deployment > Source**, select **GitHub Actions**.
3. The included [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) will automatically build and publish your dashboard live!
4. Your site will be live at: `https://<your-username>.github.io/<your-repo-name>/`

---

## Option 2: Deploy to Vercel (1-Click)

1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **Add New > Project**.
3. Import your GitHub repository.
4. The project includes [`vercel.json`](vercel.json), so leave all build settings default and click **Deploy**.
5. Your dashboard will be live on a custom `.vercel.app` domain in ~15 seconds!

---

## Option 3: Deploy to Netlify

1. Go to [netlify.com](https://netlify.com) and log in.
2. Drag and drop the folder directly into the Netlify dashboard, OR import from GitHub.
3. Publish directory: `.` (root).
4. Click **Deploy Site**.

---

## Local Development Verification
Before deploying, you can always test locally anytime by running:
```bash
./run.sh
```
Or:
```bash
open index.html
```
