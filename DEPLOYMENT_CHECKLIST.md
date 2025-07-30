# 🚀 Render Deployment Checklist

Use this checklist to ensure your HackRX API is ready for deployment on Render.

## Pre-Deployment Checklist

### ✅ Repository Setup
- [ ] Code is committed to a Git repository
- [ ] Repository is pushed to GitHub/GitLab/Bitbucket
- [ ] `.env` file is in `.gitignore` (never commit API keys!)
- [ ] `render.yaml` blueprint file is present
- [ ] `Procfile` has been removed (Heroku-specific)

### ✅ Configuration Files
- [ ] `render.yaml` - Render deployment configuration
- [ ] `requirements.txt` - Python dependencies
- [ ] `app.py` - Main application file
- [ ] `.env.template` - Template for environment variables
- [ ] `RENDER_DEPLOYMENT.md` - Deployment documentation

### ✅ Code Quality
- [ ] All imports are properly structured
- [ ] No hardcoded API keys or secrets
- [ ] Application starts with `uvicorn app:app --host 0.0.0.0 --port $PORT`
- [ ] Health check endpoint (`/`) returns valid response
- [ ] Main endpoint (`/hackrx/run`) is properly configured

## Render Platform Setup

### ✅ Account Setup
- [ ] Render account created at [render.com](https://render.com)
- [ ] GitHub/GitLab account connected to Render
- [ ] Payment method added (for paid plans if needed)

### ✅ Service Configuration
- [ ] New Blueprint/Web Service created
- [ ] Repository connected and authorized
- [ ] Build settings configured:
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- [ ] Python version set to 3.11 (or compatible)

## Environment Variables

### ✅ Required Variables
- [ ] `GEMINI_API_KEY` - Your Google Gemini API key
- [ ] `API_KEY` - Your custom API authentication key

### ✅ Optional Variables
- [ ] `ENVIRONMENT` - Set to "production"
- [ ] Custom configuration variables as needed

## Testing & Validation

### ✅ Pre-Deployment Testing
- [ ] Run `python test_render.py` - All checks pass
- [ ] Run `python test.py` - Local API tests pass
- [ ] Run `python test_sample.py` - Sample request works
- [ ] Verify all dependencies install correctly

### ✅ Post-Deployment Testing
- [ ] Service deploys successfully on Render
- [ ] Health check endpoint responds: `GET https://your-app.onrender.com/`
- [ ] Main API endpoint works: `POST https://your-app.onrender.com/hackrx/run`
- [ ] Authentication works with your API key
- [ ] Document processing works with test PDF

## Performance & Monitoring

### ✅ Performance Setup
- [ ] Service scaling configured (1-3 instances recommended)
- [ ] Resource allocation appropriate for expected load
- [ ] Auto-sleep disabled for production (paid plans)

### ✅ Monitoring Setup
- [ ] Render Dashboard monitoring enabled
- [ ] Log aggregation configured
- [ ] Health check monitoring active
- [ ] Alert notifications configured

## Production Readiness

### ✅ Security
- [ ] Strong API keys configured
- [ ] HTTPS enabled (automatic on Render)
- [ ] CORS properly configured
- [ ] Input validation implemented
- [ ] File size limits enforced

### ✅ Documentation
- [ ] API documentation accessible at `/docs`
- [ ] README updated with Render deployment info
- [ ] Environment variable documentation complete
- [ ] Troubleshooting guide available

### ✅ Backup & Recovery
- [ ] Code repository backed up
- [ ] Environment variables documented securely
- [ ] Deployment rollback plan prepared
- [ ] Disaster recovery procedure documented

## Quick Test Commands

```bash
# Test local setup
python test_render.py

# Test health endpoint
curl https://your-app.onrender.com/

# Test main API endpoint
curl -X POST "https://your-app.onrender.com/hackrx/run" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

## Troubleshooting Common Issues

### Build Failures
- [ ] Check build logs in Render Dashboard
- [ ] Verify `requirements.txt` format
- [ ] Ensure Python version compatibility
- [ ] Check for missing system dependencies

### Runtime Errors
- [ ] Check service logs for error details
- [ ] Verify environment variables are set
- [ ] Test API key validity
- [ ] Check memory/CPU resource limits

### Performance Issues
- [ ] Monitor resource usage in dashboard
- [ ] Consider upgrading service plan
- [ ] Optimize document processing
- [ ] Enable auto-scaling

---

## 🎯 Final Check

Before going live:
- [ ] All checklist items completed
- [ ] Test deployment works end-to-end
- [ ] Performance is acceptable
- [ ] Monitoring is active
- [ ] Documentation is complete

**Ready for production! 🚀**
