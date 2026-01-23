import subprocess
import json
import time
import random
import sys

# Configuration
RESOURCE_GROUP = "REDACTED_RG"
SERVER_NAME_BASE = "thedefinitive-db"
ADMIN_USER = "REDACTED_USER"
ADMIN_PASS = f"REDACTED_PASS{int(time.time())}!$"

# List of regions to try (Prioritizing those not yet explicitly failed or common for students)
# User failed: eastus, eastus2, southcentralus, swedencentral, westus3, brazilsoutheast
REGIONS_TO_TRY = [
    "centralus",
    "northcentralus",
    "westus", 
    "canadacentral",
    "westeurope",
    "northeurope",
    "uksouth",
    "francecentral",
    "japaneast",
    "southeastasia",
    "australiaeast"
]

def run_command(cmd):
    """Run a shell command and return output, checks for error."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def provision_db():
    print(f"🚀 Starting Automated Region Discovery for Azure Database Integration...")
    
    # 1. Login Check
    print("Checking Azure Login...")
    success, _ = run_command("az account show")
    if not success:
        print("❌ Not logged in. Please run 'az login' first.")
        return

    # 2. Iterate Regions
    for region in REGIONS_TO_TRY:
        server_name = f"{SERVER_NAME_BASE}-{region}-{random.randint(1000,9999)}"
        print(f"\n---------------------------------------------------------------")
        print(f"🌍 Attempting creation in region: {region}")
        print(f"   Server Name: {server_name}")
        
        cmd = f"""
        az postgres flexible-server create \\
            --resource-group {RESOURCE_GROUP} \\
            --name {server_name} \\
            --location {region} \\
            --admin-user {ADMIN_USER} \\
            --admin-password '{ADMIN_PASS}' \\
            --sku-name Standard_B1ms \\
            --tier Burstable \\
            --version 16 \\
            --storage-size 32 \\
            --yes
        """
        
        success, output = run_command(cmd)
        
        if success:
            print(f"✅ SUCCESS! Database created in {region}.")
            print(f"   Server: {server_name}")
            print(f"   User: {ADMIN_USER}")
            print(f"   Pass: {ADMIN_PASS}")
            
            # Get FQDN
            fqdn_cmd = f"az postgres flexible-server show --resource-group {RESOURCE_GROUP} --name {server_name} --query fullyQualifiedDomainName -o tsv"
            _, host = run_command(fqdn_cmd)
            host = host.strip()
            
            # Enable pgvector
            print("🧩 Enabling pgvector extension...")
            run_command(f"az postgres flexible-server parameter set --resource-group {RESOURCE_GROUP} --server-name {server_name} --name azure.extensions --value vector")
            
            # Firewall
            print("🔥 Configuring Firewall (Allow All)...")
            run_command(f"az postgres flexible-server firewall-rule create --resource-group {RESOURCE_GROUP} --name {server_name} --rule-name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255")

            conn_string = f"postgresql://{ADMIN_USER}:{ADMIN_PASS}@{host}:5432/postgres?sslmode=require"
            print(f"\n🎉 Connection String: {conn_string}")
            
            # Update .env
            with open("agent/.env", "a") as f:
                f.write(f"\nDATABASE_URL={conn_string}\n")
            print("📂 Updated agent/.env")
            
            sys.exit(0)
        else:
            print(f"❌ Failed in {region}.")
            if "RequestDisallowedByAzure" in output:
                print("   Reason: Region Disallowed by Policy.")
            elif "NoRegisteredProviderFound" in output:
                print("   Reason: Region not supported for this resource type.")
            else:
                print(f"   Error: {output[:300]}...") # Print first 300 chars of error
            
            time.sleep(2) # Brief pause

    print("\n💀 All regions failed. Please check your subscription status or try a different subscription.")

if __name__ == "__main__":
    provision_db()
