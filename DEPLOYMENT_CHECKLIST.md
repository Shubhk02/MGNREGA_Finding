# Vercel Deployment Checklist

## ✅ Pre-Deployment (Completed)

- [x] Code pushed to GitHub (commit: c4ea1c9)
- [x] District deduplication fixed (75 unique UP districts)
- [x] Vercel configuration added (vercel.json)
- [x] Environment examples created (.env.example files)
- [x] CORS configuration updated
- [x] Deployment guide created (VERCEL_DEPLOYMENT.md)

## 📋 Next Steps - Backend Deployment

### Option 1: Deploy to Railway (Recommended)

1. Visit https://railway.app and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select: `Shubhk02/MGNREGA_Finding`
4. Configure:
   - **Root Directory**: `backend`
   - Railway will auto-detect Python

5. **Add Environment Variables** (in Railway dashboard):
   ```
   MONGO_URL=mongodb+srv://shubhkaushik2003_db_user:Shubhk%401902@mgnregastorage.ts1ndu5.mongodb.net/?appName=MGNREGAStorage
   DB_NAME=mgnrega
   CORS_ORIGINS=https://your-app-name.vercel.app,http://localhost:3002,http://localhost:3000
   REDIS_URL=redis://localhost:6379
   ```

6. Railway will deploy and give you a URL like: `https://mgnrega-backend-production.up.railway.app`

7. **Note this URL** - you'll need it for Vercel!

### Option 2: Deploy to Render

1. Visit https://render.com and sign in
2. Click "New +" → "Web Service"
3. Connect GitHub repository: `Shubhk02/MGNREGA_Finding`
4. Configure:
   - **Name**: `mgnrega-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

5. Add same environment variables as Railway

6. Note the deployed URL

## 📋 Next Steps - Frontend Deployment to Vercel

1. Visit https://vercel.com and sign in
2. Click "Add New..." → "Project"
3. Import `Shubhk02/MGNREGA_Finding` from GitHub

4. **Configure Build Settings**:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build`
   - **Output Directory**: `build`
   - **Install Command**: `yarn install`

5. **Add Environment Variables** (in Vercel):
   ```
   REACT_APP_BACKEND_URL=https://your-backend-url.railway.app
   ```
   ⚠️ **IMPORTANT**: Replace with your actual Railway/Render backend URL from step 1!

6. Click "Deploy"

7. Wait for deployment to complete (~2-3 minutes)

8. Vercel will give you a URL like: `https://mgnrega-finding-shubhk02.vercel.app`

## 🔄 Update Backend CORS

After getting your Vercel URL:

1. Go back to Railway/Render dashboard
2. Update the `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://mgnrega-finding-shubhk02.vercel.app,http://localhost:3002,http://localhost:3000
   ```
   ⚠️ Replace with your actual Vercel URL!

3. Railway/Render will automatically redeploy with new settings

## ✅ Testing Your Deployment

1. Visit your Vercel URL
2. Check browser console (F12) for errors
3. Verify districts load correctly
4. Test clicking on a district to view details

### Expected Results:
- ✅ Frontend loads without errors
- ✅ Districts list shows 75 UP districts
- ✅ No CORS errors in console
- ✅ District detail pages work
- ✅ Charts and data display correctly

## 🐛 Troubleshooting

### Issue: CORS Error
**Solution**: Make sure backend `CORS_ORIGINS` includes your exact Vercel URL (with https://)

### Issue: "Failed to load districts"
**Solution**: 
1. Check `REACT_APP_BACKEND_URL` in Vercel environment variables
2. Test backend directly: `https://your-backend.railway.app/api/districts?state_code=UP`

### Issue: 404 on Page Refresh
**Solution**: The `vercel.json` file should handle this - make sure it's in the root directory

### Issue: Build Fails on Vercel
**Solution**:
1. Check build logs in Vercel dashboard
2. Verify `package.json` has all dependencies
3. Test `yarn build` locally first

## 📊 Your Current Setup

- **GitHub Repo**: https://github.com/Shubhk02/MGNREGA_Finding
- **Latest Commit**: c4ea1c9 - "feat: Add Vercel deployment support and fix district deduplication"
- **MongoDB**: Already configured (Atlas cluster)
- **Backend Status**: Ready to deploy
- **Frontend Status**: Ready to deploy

## 🎯 Quick Links

- Railway: https://railway.app
- Render: https://render.com
- Vercel: https://vercel.com
- Your GitHub Repo: https://github.com/Shubhk02/MGNREGA_Finding

## 📝 Notes

- Backend must be deployed BEFORE frontend (you need the backend URL for frontend env)
- After any environment variable change, services will auto-redeploy
- Free tiers are sufficient for testing/development
- MongoDB Atlas is already set up and working

---

**Ready to deploy!** Start with the backend (Railway/Render), then deploy the frontend (Vercel).
