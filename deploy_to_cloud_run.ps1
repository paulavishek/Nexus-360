# Cloud Run deployment script for PM Chatbot for Windows PowerShell

Write-Host "=== PM Chatbot - Google Cloud Run Deployment ===" -ForegroundColor Green
Write-Host "This script will help you deploy your chatbot to Google Cloud Run."

# 1. Check for gcloud CLI
Write-Host "`nChecking for Google Cloud SDK..." -ForegroundColor Yellow
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "Google Cloud SDK (gcloud) is not installed!" -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# 2. Check if user is logged in
Write-Host "`nChecking authentication..." -ForegroundColor Yellow
$ACCOUNT = & gcloud config get-value account 2>$null
if (-not $ACCOUNT) {
    Write-Host "You are not logged in to Google Cloud. Please login:"
    & gcloud auth login
}
else {
    Write-Host "Logged in as: $ACCOUNT" -ForegroundColor Green
}

# 3. Get or confirm project ID
Write-Host "`nSetting up project..." -ForegroundColor Yellow
$PROJECT_ID = & gcloud config get-value project 2>$null
if (-not $PROJECT_ID) {
    Write-Host "No default project set."
    $PROJECT_ID = Read-Host "Enter your Google Cloud project ID"
    & gcloud config set project $PROJECT_ID
}
else {
    $CHANGE = Read-Host "Using project [$PROJECT_ID]. Change? (y/N)"
    if ($CHANGE -eq "y" -or $CHANGE -eq "Y") {
        $PROJECT_ID = Read-Host "Enter your Google Cloud project ID"
        & gcloud config set project $PROJECT_ID
    }
}

Write-Host "Using project: $PROJECT_ID" -ForegroundColor Green

# 4. Enable required APIs
Write-Host "`nEnabling required Google Cloud APIs..." -ForegroundColor Yellow
& gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com

# 5. Create a Docker repository
Write-Host "`nSetting up Artifact Registry..." -ForegroundColor Yellow
$REGION = "us-central1"  # Default region
$INPUT_REGION = Read-Host "Enter region for deployment [$REGION]"
if ($INPUT_REGION) { $REGION = $INPUT_REGION }

$REPO_NAME = "pm-chatbot"
& gcloud artifacts repositories create $REPO_NAME `
    --repository-format=docker `
    --location=$REGION `
    --description="Docker repository for PM Chatbot"

# 6. Build and push the Docker image
Write-Host "`nBuilding and pushing Docker image..." -ForegroundColor Yellow
$IMAGE_NAME = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/pm-chatbot:v1"

# Make sure .env file exists
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found. Creating one from .env.example" -ForegroundColor Red
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your actual configuration before continuing!" -ForegroundColor Yellow
    Read-Host "Press Enter to continue after editing your .env file..."
}

# Build the Docker image
& gcloud builds submit --tag $IMAGE_NAME

# 7. Set up Secret Manager for environment variables
Write-Host "`nSetting up secrets in Secret Manager..." -ForegroundColor Yellow

# Create secrets from .env file
$SECRET_NAME = "pm-chatbot-env"

# Check if secret already exists
$SECRET_EXISTS = $null
try {
    $SECRET_EXISTS = & gcloud secrets describe $SECRET_NAME 2>$null
}
catch {}

if ($SECRET_EXISTS) {
    Write-Host "Secret $SECRET_NAME already exists. Updating..."
    & gcloud secrets versions add $SECRET_NAME --data-file=.env
}
else {
    Write-Host "Creating new secret $SECRET_NAME..."
    & gcloud secrets create $SECRET_NAME --data-file=.env
}

# 8. Deploy to Cloud Run
Write-Host "`nDeploying to Cloud Run..." -ForegroundColor Yellow
$SERVICE_NAME = "pm-chatbot"

& gcloud run deploy $SERVICE_NAME `
    --image=$IMAGE_NAME `
    --platform=managed `
    --region=$REGION `
    --allow-unauthenticated `
    --port=8080 `
    --set-secrets="/app/.env=pm-chatbot-env:latest" `
    --memory=512Mi `
    --cpu=1

# 9. Show deployment info
Write-Host "`nDeployment complete!" -ForegroundColor Green
$URL = & gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'

Write-Host "Your chatbot is now available at: $URL" -ForegroundColor Green
Write-Host "Remember to add this URL to your ALLOWED_HOSTS in your .env file if needed." -ForegroundColor Yellow
Write-Host "You may want to adjust the memory and CPU settings based on your needs." -ForegroundColor Yellow
