# HackRX Project Deployment Guide

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn package manager
- Git
- Account on deployment platform (Render, Vercel, Netlify, etc.)

## Local Development Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd HackRX
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run development server:
```bash
npm run dev
# or
yarn dev
```

## Build Process

1. Create production build:
```bash
npm run build
# or
yarn build
```

2. Test production build locally:
```bash
npm start
# or
yarn start
```

## Deployment Options

### Option 1: Render.com Deployment

1. **Connect Repository:**
   - Go to [Render.com](https://render.com)
   - Sign up/Login with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build Settings:**
   - Build Command: `npm run build`
   - Start Command: `npm start`
   - Node Version: `16` (or your preferred version)

3. **Environment Variables:**
   - Add all required environment variables in Render dashboard
   - Settings → Environment → Add environment variable

4. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy

### Option 2: Vercel Deployment

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy:**
```bash
vercel --prod
```

3. **Configure:**
   - Add environment variables in Vercel dashboard
   - Configure build settings if needed

### Option 3: Netlify Deployment

1. **Build for static deployment:**
```bash
npm run build
npm run export
```

2. **Deploy:**
   - Drag and drop `out` folder to Netlify
   - Or connect GitHub repository in Netlify dashboard

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=your_database_url

# Authentication
NEXTAUTH_SECRET=your_nextauth_secret
NEXTAUTH_URL=your_deployment_url

# API Keys
API_KEY=your_api_key

# Other configurations
NODE_ENV=production
```

## Post-Deployment Steps

1. **Verify deployment:**
   - Check application loads correctly
   - Test all major features
   - Verify API endpoints

2. **Set up monitoring:**
   - Configure error tracking
   - Set up uptime monitoring
   - Enable logging

3. **Configure custom domain (optional):**
   - Add custom domain in platform settings
   - Update DNS records
   - Enable SSL certificate

## Troubleshooting

### Common Issues:

1. **Build Failures:**
   - Check Node.js version compatibility
   - Verify all dependencies are listed in package.json
   - Review build logs for specific errors

2. **Environment Variables:**
   - Ensure all required variables are set
   - Check for typos in variable names
   - Verify sensitive data is not committed to repository

3. **Database Connection:**
   - Verify database URL is correct
   - Check network access permissions
   - Ensure database is accessible from deployment platform

4. **Performance Issues:**
   - Enable compression
   - Optimize images and assets
   - Configure caching headers

## Maintenance

1. **Regular Updates:**
   - Keep dependencies updated
   - Monitor security vulnerabilities
   - Update Node.js version as needed

2. **Backup:**
   - Regular database backups
   - Version control for code changes
   - Document configuration changes

3. **Monitoring:**
   - Set up alerts for downtime
   - Monitor application performance
   - Track error rates and user metrics

## Quick Deployment Commands

```bash
# Full deployment pipeline
git add .
git commit -m "Deploy: your message"
git push origin main

# Force rebuild on Render
curl -X POST "https://api.render.com/deploy/srv-YOUR_SERVICE_ID"
```

## Support

For deployment issues:
1. Check platform-specific documentation
2. Review deployment logs
3. Contact platform support if needed

---

**Last Updated:** [Current Date]
**Platform:** Multi-platform compatible
**Status:** Production Ready
