#!/bin/bash

# Configuration
RESOURCE_GROUP="REDACTED_RG"
BACKEND_APP_NAME="banking-rag-auth-api"
FRONTEND_APP_NAME="banking-rag-web"
PLAN_NAME="banking-rag-plan"

# List of regions to try for App Service
REGIONS=("eastus" "centralus" "northcentralus" "southcentralus" "westus" "westus2" "westeurope" "northeurope" "japaneast" "inframundo")

echo "🚀 Starting Azure Hosting Setup (Free Tier)..."

# 1. Login check
if ! az account show &> /dev/null; then
    echo "❌ not logged in. Run 'az login' first."
    exit 1
fi

# 2. Resource Group (Already exists in EastUS usually)
echo "📦 Using Resource Group '$RESOURCE_GROUP'..."
# Check if exists, if not create in eastus (default)
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    az group create --name $RESOURCE_GROUP --location eastus
fi

# 3. Backend: App Service (Try Regions)
LOCATION=""
PLAN_CREATED=false

for REGION in "${REGIONS[@]}"; do
    echo "� Attempting to create App Service Plan in '$REGION'..."
    
    if az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku F1 --is-linux --location $REGION &> /dev/null; then
        echo "✅ Success! Plan created in '$REGION'."
        LOCATION=$REGION
        PLAN_CREATED=true
        break
    else
        echo "❌ Failed in '$REGION'. Disallowed or quota reached."
    fi
done

if [ "$PLAN_CREATED" = false ]; then
    echo "💀 All regions failed for App Service Plan. Cannot proceed."
    exit 1
fi

echo "🐍 Creating Web App '$BACKEND_APP_NAME' in '$LOCATION'..."
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $BACKEND_APP_NAME --runtime "PYTHON:3.10"

echo "⚙️ Configuring Backend Settings..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $BACKEND_APP_NAME --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    PYTHON_ENABLE_GUNICORN_MULTIWORKERS=true \
    WEBSITES_PORT=8000

# 4. Frontend: Static Web App (Try Regions)
# Static Web Apps are global but need a location for metadata. We use the same as backend or fallback.
echo "⚛️ Creating Static Web App '$FRONTEND_APP_NAME'..."
if ! az staticwebapp create --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --location $LOCATION --sku Free; then
     # Fallback for SWA if specific region fails (SWA supports fewer regions than App Service sometimes)
     echo "⚠️ creating in primary location failed, trying 'westeurope'..."
     az staticwebapp create --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --location "westeurope" --sku Free
fi

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
