#!/bin/bash

# GCP Deployment Script for Analytics Viewer
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Configuration
PROJECT_ID=${1:-"analytics-viewer-$(date +%s)"}
REGION=${2:-"us-central1"}

echo "🚀 Starting deployment to GCP"
echo "📋 Project ID: $PROJECT_ID"
echo "🌍 Region: $REGION"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI (gcloud) is not installed."
    echo "📥 Please install it first: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null; then
    echo "🔐 Please authenticate with Google Cloud first:"
    echo "   gcloud auth login"
    exit 1
fi

# Set project
echo "⚙️  Setting up project configuration..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com \
                       run.googleapis.com \
                       containerregistry.googleapis.com \
                       secretmanager.googleapis.com

echo "🔐 Please set up your environment variables in Secret Manager:"
echo "   You need to create the following secrets:"
echo "   - openai-api-key: Your OpenAI API key"
echo "   - google-api-key: Your Google API key (for web search)"
echo "   - google-cse-id: Your Google Custom Search Engine ID"
echo "   - clickhouse-host: Your ClickHouse host"
echo "   - clickhouse-password: Your ClickHouse password"
echo "   - clickhouse-database: Your ClickHouse database name"
echo ""
echo "   Example commands:"
echo "   echo -n 'your_openai_api_key' | gcloud secrets create openai-api-key --data-file=-"
echo ""

read -p "Press Enter after you've created all the secrets..."

# Deploy backend
echo "🏗️  Deploying backend to Cloud Run..."
cd backend

# Submit build
gcloud builds submit --config cloudbuild.yaml

echo "✅ Backend deployment completed!"

# Get backend URL
BACKEND_URL=$(gcloud run services describe analytics-backend --region=$REGION --format='value(status.url)')
echo "🔗 Backend URL: $BACKEND_URL"

# Deploy frontend
echo "🎨 Deploying frontend to Cloud Run..."
cd ../frontend

# Build with backend URL
gcloud builds submit --config cloudbuild.yaml --substitutions=_BACKEND_URL="$BACKEND_URL/api"

echo "✅ Frontend deployment completed!"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe analytics-frontend --region=$REGION --format='value(status.url)')
echo "🔗 Frontend URL: $FRONTEND_URL"

echo ""
echo "🎉 Deployment completed successfully!"
echo "📱 Frontend: $FRONTEND_URL"
echo "🔧 Backend API: $BACKEND_URL"
echo "📖 API Documentation: $BACKEND_URL/docs"
echo ""
echo "🔍 To view logs:"
echo "   Backend: gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=analytics-backend' --limit 50"
echo "   Frontend: gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=analytics-frontend' --limit 50"