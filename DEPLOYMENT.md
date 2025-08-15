# Deployment Guide - Vercel

## Prerequisites
- Node.js 18+ installed
- Git repository
- Vercel account

## Steps to Deploy

### 1. Via Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name: embeddedchat-frontend
# - In which directory is your code located? ./
```

### 2. Via Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub/GitLab/Bitbucket
3. Click "New Project"
4. Import your repository
5. Set build settings:
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
   - Root Directory: `frontend`

### 3. Environment Variables
If your app needs environment variables:
1. Go to your project dashboard on Vercel
2. Navigate to Settings > Environment Variables
3. Add your variables (e.g., API_URL, etc.)

### 4. Custom Domain (Optional)
1. In project settings, go to Domains
2. Add your custom domain
3. Configure DNS as instructed

## Build Optimization
- The project is configured for optimal Vite builds
- Static assets are properly handled
- Source maps are disabled for production

## Troubleshooting
- Ensure all dependencies are in package.json
- Check build logs in Vercel dashboard
- Verify all environment variables are set
- Make sure the build command succeeds locally first
