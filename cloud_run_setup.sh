#!/bin/bash
# Cloud Run deployment script for PM Chatbot

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PM Chatbot - Google Cloud Run Deployment ===${NC}"
echo "This script will help you deploy your chatbot to Google Cloud Run."

# 1. Check for gcloud CLI
echo -e "\n${YELLOW}Checking for Google Cloud SDK...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Google Cloud SDK (gcloud) is not installed!${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# 2. Check if user is logged in
echo -e "\n${YELLOW}Checking authentication...${NC}"
ACCOUNT=$(gcloud config get-value account 2>/dev/null)
if [ -z "$ACCOUNT" ]; then
    echo "You are not logged in to Google Cloud. Please login:"
    gcloud auth login
else
    echo -e "${GREEN}Logged in as: $ACCOUNT${NC}"
fi

# 3. Get or confirm project ID
echo -e "\n${YELLOW}Setting up project...${NC}"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "No default project set."
    read -p "Enter your Google Cloud project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
else
    read -p "Using project [$PROJECT_ID]. Change? (y/N): " CHANGE
    if [[ $CHANGE == [Yy]* ]]; then
        read -p "Enter your Google Cloud project ID: " PROJECT_ID
        gcloud config set project $PROJECT_ID
    fi
fi

echo -e "${GREEN}Using project: $PROJECT_ID${NC}"

# 4. Enable required APIs
echo -e "\n${YELLOW}Enabling required Google Cloud APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com

# 5. Create a Docker repository
echo -e "\n${YELLOW}Setting up Artifact Registry...${NC}"
REGION="us-central1"  # Default region
read -p "Enter region for deployment [$REGION]: " INPUT_REGION
REGION=${INPUT_REGION:-$REGION}

REPO_NAME="pm-chatbot"
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for PM Chatbot"

# 6. Build and push the Docker image
echo -e "\n${YELLOW}Building and pushing Docker image...${NC}"
IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/pm-chatbot:v1"

# Make sure .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}.env file not found. Creating one from .env.example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your actual configuration before continuing!${NC}"
    read -p "Press Enter to continue after editing your .env file..."
fi

# Build the Docker image
gcloud builds submit --tag $IMAGE_NAME

# 7. Set up Secret Manager for environment variables
echo -e "\n${YELLOW}Setting up secrets in Secret Manager...${NC}"

# Create secrets from .env file
SECRET_NAME="pm-chatbot-env"

# Check if secret already exists
if gcloud secrets describe $SECRET_NAME 2>/dev/null; then
    echo "Secret $SECRET_NAME already exists. Updating..."
    gcloud secrets versions add $SECRET_NAME --data-file=.env
else
    echo "Creating new secret $SECRET_NAME..."
    gcloud secrets create $SECRET_NAME --data-file=.env
fi

# 8. Deploy to Cloud Run
echo -e "\n${YELLOW}Deploying to Cloud Run...${NC}"
SERVICE_NAME="pm-chatbot"

gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_NAME \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --port=8080 \
    --set-secrets="/app/.env=pm-chatbot-env:latest" \
    --memory=512Mi \
    --cpu=1

# 9. Show deployment info
echo -e "\n${GREEN}Deployment complete!${NC}"
URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "${GREEN}Your chatbot is now available at: $URL${NC}"
echo -e "${YELLOW}Remember to add this URL to your ALLOWED_HOSTS in your .env file if needed.${NC}"
echo -e "${YELLOW}You may want to adjust the memory and CPU settings based on your needs.${NC}"
