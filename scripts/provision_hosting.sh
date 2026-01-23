#!/bin/bash

# Configuration
RESOURCE_GROUP="REDACTED_RG"
LOCATION="eastus2" # Free tier friendly region
BACKEND_APP_NAME="banking-rag-auth-api-$(date +%s)"
FRONTEND_APP_NAME="banking-rag-web-$(date +%s)"

echo "🚀 Starting Azure Hosting Setup (Free Tier)..."

# 1. Login check
if ! az account show &> /dev/null; then
    echo "❌ not logged in. Run 'az login' first."
    exit 1
fi

# 2. Resource Group
echo "📦 Ensuring Resource Group '$RESOURCE_GROUP'..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# 3. Backend: App Service (Python / Linux / Free F1)
PLAN_NAME="banking-rag-plan"
echo "🐍 Creating App Service Plan '$PLAN_NAME' (F1 Free)..."
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku F1 --is-linux

echo "🐍 Creating Web App '$BACKEND_APP_NAME'..."
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $BACKEND_APP_NAME --runtime "PYTHON:3.10"

echo "⚙️ Configuring Backend Settings..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $BACKEND_APP_NAME --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    PYTHON_ENABLE_GUNICORN_MULTIWORKERS=true \
    WEBSITES_PORT=8000

# 4. Frontend: Static Web App (React / Free)
echo "⚛️ Creating Static Web App '$FRONTEND_APP_NAME'..."
az staticwebapp create --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --location $LOCATION --sku Free

# 5. Output Secrets
echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo "👉 Backend URL: https://$BACKEND_APP_NAME.azurewebsites.net"
echo "👉 Frontend URL: (Check Portal or below)"
echo ""
echo "🔐 SECRETS FOR GITHUB:"
echo "--------------------------------------------------"

# Get Web App Publish Profile
PROFILE=$(az webapp deployment list-publishing-profiles --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --xml)
echo "1. AZURE_WEBAPP_PUBLISH_PROFILE:"
echo "   (Copy the content below as a single line or XML block)"
echo "$PROFILE"
echo ""

# Get Static Web App Token
TOKEN=$(az staticwebapp secrets list --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.apiKey" -o tsv)
echo "2. AZURE_STATIC_WEB_APPS_API_TOKEN:"
echo "   $TOKEN"
echo ""
echo "--------------------------------------------------"
echo "ℹ️  Add these secrets to your GitHub Repo -> Settings -> Secrets and variables -> Actions"
