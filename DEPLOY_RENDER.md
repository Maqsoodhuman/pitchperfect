# Deploying PitchPerfect to Render

This guide walks you through deploying PitchPerfect to Render using Docker.

## Prerequisites

1. A [Render](https://render.com) account (free tier available)
2. A GitHub/GitLab repository with your code
3. Your environment variables ready (API keys, etc.)

## Deployment Steps

### Option 1: Deploy via Render Blueprint (Recommended)

1. **Push your code to GitHub/GitLab**
   ```bash
   git init
   git add .
   git commit -m "Add Render deployment files"
   git remote add origin https://github.com/YOUR_USERNAME/pitchperfect.git
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub/GitLab repository
   - Select the `render.yaml` file

3. **Set Environment Variables**
   In the Render dashboard, add these environment variables (from your `.env` file):
   
   | Key | Value |
   |-----|-------|
   | `OPENAI_API_KEY` | Your OpenAI API key |
   | `SUPABASE_URL` | Your Supabase project URL |
   | `SUPABASE_ANON_KEY` | Your Supabase anonymous key |
   | `SUPABASE_SERVICE_KEY` | Your Supabase service role key |
   | `LANGSMITH_API_KEY` | Your LangSmith API key |
   | `LANGSMITH_PROJECT` | `pitchperfect` |
   | `LANGSMITH_TRACING` | `true` |
   | `LANGSMITH_ENDPOINT` | `https://api.smith.langchain.com` |

4. **Deploy**
   - Click "Apply Blueprint"
   - Wait for the Docker image to build (~5-10 minutes)
   - Your app will be live at `https://pitchperfect.onrender.com`

### Option 2: Deploy via Render Dashboard (Manual)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment files"
   git push origin main
   ```

2. **Create Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your repository
   - Configure:
     - **Name**: `pitchperfect`
     - **Region**: Oregon (or closest to you)
     - **Runtime**: Docker
     - **Instance Type**: Free

3. **Set Environment Variables**
   Add all the environment variables listed in Option 1 above.

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build (~5-10 minutes)

## After Deployment

Once deployed, your app will be available at:
```
https://pitchperfect.onrender.com
```

### Free Tier Limitations

| Feature | Free Tier Limit |
|---------|-----------------|
| Sleep after inactivity | 15 minutes |
| Build minutes | 500/month |
| Bandwidth | 100GB/month |
| Disk | 1GB |

For personal/side projects, the free tier is usually sufficient.

## Troubleshooting

### Build Fails
- Check the build logs in Render dashboard
- Ensure all environment variables are set
- Verify the Dockerfile syntax

### App Crashes on Start
- Check the Tectonic installation in logs
- Verify environment variables are loaded correctly
- Check the logs: Render Dashboard → Your Service → Logs

### LaTeX Compilation Fails
- Check that Tectonic is in PATH
- Verify the `/root/.cache/Tectonic` directory exists

### Database Connection Fails
- Verify Supabase URL and keys are correct
- Check Supabase project is active
- Verify API keys have correct permissions

## Updating Your Deployment

1. Make changes to your code
2. Push to GitHub
3. Render will automatically rebuild and deploy

Or manually trigger a deploy:
```bash
render deploy --service pitchperfect
```

## Local Development with Docker

To test the Docker setup locally:

```bash
# Build the image
docker build -t pitchperfect .

# Run with environment variables
docker run -p 8501:8501 \
  -e OPENAI_API_KEY="your-key" \
  -e SUPABASE_URL="your-url" \
  -e SUPABASE_ANON_KEY="your-key" \
  -e SUPABASE_SERVICE_KEY="your-key" \
  pitchperfect
```

Then open http://localhost:8501
