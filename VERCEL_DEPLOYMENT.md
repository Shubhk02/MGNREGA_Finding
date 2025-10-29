# MGNREGA Dashboard - Vercel Deployment Guide

## Prerequisites
- GitHub repository with your code
- Vercel account (sign up at https://vercel.com)
- MongoDB Atlas cluster URL

## Deployment Steps

### 1. Deploy Backend (MongoDB Atlas + Render/Railway)

Since Vercel doesn't support persistent Python backends well, deploy your backend separately:

#### Option A: Railway
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your MGNREGA_Finding repository
4. Set root directory to `backend`
5. Add environment variables:
   - `MONGO_URL`: Your MongoDB Atlas connection string
   - `DB_NAME`: `mgnrega_db`
   - `CORS_ORIGINS`: `https://your-app.vercel.app,http://localhost:3002`
   - `REDIS_URL`: (optional) Your Redis URL
6. Railway will auto-detect Python and deploy
7. Note your backend URL (e.g., `https://your-app.railway.app`)

#### Option B: Render
1. Go to https://render.com
2. Create new "Web Service"
3. Connect your GitHub repo
4. Configure:
   - Name: `mgnrega-backend`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as Railway)
6. Note your backend URL

### 2. Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build`
   - **Output Directory**: `build`
   - **Install Command**: `yarn install`

5. Add Environment Variables:
   - `REACT_APP_BACKEND_URL`: Your backend URL (from Railway/Render)
   - Example: `https://mgnrega-backend.railway.app`

6. Click "Deploy"

### 3. Update Backend CORS

After deployment, update your backend's `CORS_ORIGINS` environment variable to include your Vercel URL:
```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3002,http://localhost:3000
```

### 4. Test Your Deployment

Visit your Vercel URL and verify:
- ✅ Frontend loads without errors
- ✅ Districts list appears
- ✅ No CORS errors in browser console
- ✅ District detail pages work

## Environment Variables Summary

### Backend (Railway/Render)
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=mgnrega_db
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3002
REDIS_URL=redis://default:password@host:port (optional)
DATA_GOV_API_KEY=your_api_key (optional)
```

### Frontend (Vercel)
```env
REACT_APP_BACKEND_URL=https://your-backend.railway.app
```

## Troubleshooting

### CORS Errors
- Ensure backend `CORS_ORIGINS` includes your Vercel URL
- Check that backend is using both `http://` and `https://` if needed

### Districts Not Loading
- Verify `REACT_APP_BACKEND_URL` is set correctly in Vercel
- Check browser console for API errors
- Test backend endpoint directly: `https://your-backend.railway.app/api/districts?state_code=UP`

### Build Failures
- Ensure all dependencies are in `package.json`
- Check build logs in Vercel dashboard
- Verify `yarn build` works locally

### 404 on Refresh
- The `vercel.json` routing config should handle this
- Ensure `vercel.json` is in the repository root

## Custom Domain (Optional)

1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records as instructed
5. Update backend `CORS_ORIGINS` to include new domain

## Monitoring

- **Frontend**: Vercel Dashboard → Analytics
- **Backend**: Railway/Render Dashboard → Metrics
- **Database**: MongoDB Atlas → Metrics

## Support

For issues:
- Check Vercel deployment logs
- Check backend service logs
- Verify environment variables are set correctly
- Test API endpoints manually using browser or Postman
