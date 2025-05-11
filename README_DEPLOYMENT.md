# Deploying PM Chatbot to Google Cloud Run

This document provides instructions for deploying your PM Chatbot (with OpenAI, Gemini, and Google Search capabilities) to Google Cloud Run.

## Prerequisites

1. A Google Cloud Platform account
2. Google Cloud SDK (gcloud) installed on your local machine
3. Docker installed on your local machine (for local testing)
4. Your API keys:
   - OpenAI API key
   - Google Gemini API key
   - Google Search API key (if using search functionality)

## Deployment Options

### Option 1: Automated Deployment (PowerShell)

For Windows users, we've provided a PowerShell script that automates the deployment process:

1. Make sure you have the Google Cloud SDK installed
2. Open PowerShell and navigate to your project directory
3. Run the deployment script:

```powershell
.\deploy_to_cloud_run.ps1
```

The script will:
- Check for the necessary prerequisites
- Help you log in to Google Cloud if needed
- Set up your Google Cloud project
- Build and deploy your application to Cloud Run
- Set up your environment variables as secrets

### Option 2: Automated Deployment (Bash)

For Linux/Mac users, we've provided a bash script that automates the deployment process:

1. Make sure you have the Google Cloud SDK installed
2. Open a terminal and navigate to your project directory
3. Make the script executable and run it:

```bash
chmod +x cloud_run_setup.sh
./cloud_run_setup.sh
```

### Option 3: Manual Deployment

If you prefer to deploy manually, follow these steps:

1. **Set up your Google Cloud Project**:
   ```bash
   gcloud auth login
   gcloud projects create [PROJECT_ID] --name="PM Chatbot"
   gcloud config set project [PROJECT_ID]
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
   ```

2. **Create a Docker repository**:
   ```bash
   gcloud artifacts repositories create pm-chatbot \
     --repository-format=docker \
     --location=us-central1 \
     --description="Docker repository for PM Chatbot"
   ```

3. **Build and push your Docker image**:
   ```bash
   gcloud builds submit --tag us-central1-docker.pkg.dev/[PROJECT_ID]/pm-chatbot/pm-chatbot:v1
   ```

4. **Set up your environment variables as secrets**:
   ```bash
   gcloud secrets create pm-chatbot-env --data-file=.env
   ```

5. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy pm-chatbot \
     --image=us-central1-docker.pkg.dev/[PROJECT_ID]/pm-chatbot/pm-chatbot:v1 \
     --platform=managed \
     --region=us-central1 \
     --allow-unauthenticated \
     --port=8080 \
     --set-secrets="/app/.env=pm-chatbot-env:latest" \
     --memory=512Mi \
     --cpu=1
   ```

## Environment Configuration

Before deploying, ensure your `.env` file is properly configured. You can start with the `.env.example` file and customize it:

1. Set `DJANGO_SECRET_KEY` to a secure random string
2. Set `DEBUG=False` for production
3. Update `ALLOWED_HOSTS` to include your Cloud Run domain (will be something like `pm-chatbot-abcdefg-uc.a.run.app`)
4. Add your API keys:
   - `OPENAI_API_KEY`
   - `GOOGLE_GEMINI_API_KEY`
   - `GOOGLE_SEARCH_API_KEY` (if using search)
   - `GOOGLE_SEARCH_ENGINE_ID` (if using search)

## Post-Deployment

After successful deployment:

1. Your app will be accessible at the URL provided in the deployment output
2. You may need to run database migrations if using a persistent database
3. Monitor your application's performance in the Google Cloud Console

## Troubleshooting

If you encounter issues:

1. **Check Logs**: View the logs in the Google Cloud Console
2. **WebSocket Issues**: Make sure your Cloud Run configuration supports WebSockets
3. **API Key Issues**: Verify your API keys are correctly set in the environment variables

## Cost Management

For a resume showcase project with minimal traffic:

1. Cloud Run uses a pay-per-use model, charging only when your service is handling requests
2. The free tier includes:
   - 2 million requests per month
   - 360,000 GB-seconds of memory
   - 180,000 vCPU-seconds of compute time
3. For minimal usage, your costs should remain within the free tier

To further optimize costs:
- Set minimum instances to 0 (default)
- Use the smallest container size possible (0.5 CPU, 512MB RAM is often sufficient)
- If using additional Google Cloud services, configure them with cost control in mind
