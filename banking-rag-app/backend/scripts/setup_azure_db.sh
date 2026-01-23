#!/bin/bash

# Configuration
RESOURCE_GROUP="REDACTED_RG"
RG_LOCATION="eastus" # Resource Group is locked to eastus
SERVER_LOCATION="southcentralus" # Trying southcentralus
SERVER_NAME="REDACTED_SERVER_$(date +%s)" # Unique name
ADMIN_USER="REDACTED_USER"
# Generate a random password
ADMIN_PASS="REDACTED_PASS$(date +%s)!$"

echo "🚀 Starting Azure Setup..."

# 1. Login check
if ! az account show &> /dev/null; then
    echo "❌ You are not logged in. Please run 'az login --use-device-code' manually first."
    exit 1
fi

echo "✅ Logged in."

# 2. Create Resource Group (Ensure it exists in its original location)
echo "📦 Ensuring Resource Group '$RESOURCE_GROUP' exists in '$RG_LOCATION'..."
az group create --name $RESOURCE_GROUP --location $RG_LOCATION

# 3. Create Flexible Server
# B1MS, 32GB, Dev/Test workload (burstable)
echo "🗄️ Creating PostgreSQL Flexible Server '$SERVER_NAME' in '$SERVER_LOCATION'..."
az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $SERVER_NAME \
    --location $SERVER_LOCATION \
    --admin-user $ADMIN_USER \
    --admin-password $ADMIN_PASS \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 16 \
    --yes

# 4. Configure Firewall (Allow all IPs for demo simplicity or specific IP)
echo "🔥 Configuring Firewall..."
# Ensure local access - for dev env, we might need to open 0.0.0.0-255.255.255.255 OR just allow the current IP
# Safest for cloud dev envs (like Codespaces) is often allowing all Azure services or finding the outbound IP.
# For simplicity in this demo environment: Allow all (Classic 'Allow all IPs' for dev)
az postgres flexible-server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --name $SERVER_NAME \
    --rule-name AllowAll \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 255.255.255.255

# 5. Enable pgvector
echo "🧩 Enabling pgvector extension..."
az postgres flexible-server parameter set \
    --resource-group $RESOURCE_GROUP \
    --server-name $SERVER_NAME \
    --subscription $(az account show --query id -o tsv) \
    --name azure.extensions \
    --value vector

# 6. Output Connection Info
HOST=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $SERVER_NAME --query fullyQualifiedDomainName -o tsv)

echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "Server: $HOST"
echo "User: $ADMIN_USER"
echo "Pass: $ADMIN_PASS"
echo "Connection String: postgresql://$ADMIN_USER:$ADMIN_PASS@$HOST:5432/postgres?sslmode=require"
echo "=============================================="

# Write to .env.db_setup (temporary)
echo "DATABASE_URL=postgresql://$ADMIN_USER:$ADMIN_PASS@$HOST:5432/postgres?sslmode=require" > .env.db_setup
