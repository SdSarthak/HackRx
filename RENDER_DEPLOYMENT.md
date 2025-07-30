# Render Deployment Guide

This guide will help you deploy the HackRX Policy QA API to Render.

## Quick Deploy (Recommended)

### Option 1: Using render.yaml (Blueprint)

1. **Fork this repository** to your GitHub account
2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub account and select the forked repository
   - Render will automatically detect the `render.yaml` configuration

3. **Set Environment Variables**:
   - In the Render Dashboard, go to your service settings
   - Add the following environment variables:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     API_KEY=your_secure_api_key_here
     ENVIRONMENT=production
     ```

4. **Deploy**: 
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Your API will be available at: `https://your-service-name.onrender.com`

### Option 2: Manual Web Service

1. **Create New Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build Settings**:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Settings**:
   ```
   Python Version: 3.11.0
   ```

4. **Environment Variables**:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   API_KEY=your_secure_api_key_here
   ENVIRONMENT=production
   ```

5. **Deploy**: Click "Create Web Service"

## Configuration Details

### render.yaml Blueprint
The included `render.yaml` file configures:
- **Python 3.11** runtime
- **Auto-scaling**: 1-3 instances based on load
- **Environment variables**: Configured in Render Dashboard
- **Build optimization**: Efficient dependency installation
- **Health checks**: Automatic monitoring

### Resource Allocation
- **Memory**: 512MB (can be upgraded)
- **CPU**: Shared (can be upgraded to dedicated)
- **Storage**: 1GB temporary disk for document processing
- **Bandwidth**: Unlimited

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key |
| `API_KEY` | No | Custom API authentication key |
| `ENVIRONMENT` | No | Set to "production" for production deployment |

## Deployment Features

### Automatic Deployments
- **Git Integration**: Auto-deploy on push to main branch
- **Preview Deployments**: Test changes with pull request previews
- **Rollback**: Easy rollback to previous versions

### Monitoring & Logs
- **Real-time Logs**: View application logs in Render Dashboard
- **Metrics**: CPU, memory, and request metrics
- **Health Checks**: Automatic health monitoring
- **Alerts**: Email notifications for service issues

### Custom Domain
1. Go to your service settings in Render Dashboard
2. Click "Custom Domain"
3. Add your domain (e.g., `api.yourdomain.com`)
4. Configure DNS records as instructed
5. SSL certificate is automatically provided

## Testing Your Deployment

Once deployed, test your API:

```bash
# Health check
curl https://your-service-name.onrender.com/

# API test
curl -X POST "https://your-service-name.onrender.com/hackrx/run" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": ["What is the grace period?"]
  }'
```

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check build logs in Render Dashboard
   - Ensure `requirements.txt` is properly formatted
   - Verify Python version compatibility

2. **Runtime Errors**:
   - Check service logs for error details
   - Verify environment variables are set correctly
   - Ensure GEMINI_API_KEY is valid

3. **Performance Issues**:
   - Consider upgrading to paid plans for more resources
   - Optimize document processing for large files
   - Enable auto-scaling for traffic spikes

### Getting Help
- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Service Logs**: Available in Render Dashboard
- **Support**: Contact Render support for platform issues

## Cost Optimization

### Free Tier
- **Free hours**: 750 hours/month
- **Sleep mode**: Service sleeps after 15 minutes of inactivity
- **Cold starts**: 30-60 second delay when waking up

### Paid Plans
- **Starter**: $7/month - Always on, faster builds
- **Standard**: $25/month - More resources, priority support
- **Pro**: $85/month - Dedicated resources, advanced features

## Security Best Practices

1. **Environment Variables**: Never commit API keys to repository
2. **API Authentication**: Use strong API keys for production
3. **HTTPS**: Always enabled by default on Render
4. **Access Control**: Configure proper CORS settings
5. **Monitoring**: Enable logging and monitoring for security events

---

Your HackRX API is now ready for production on Render! 🚀
