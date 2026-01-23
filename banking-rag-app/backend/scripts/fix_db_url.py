import urllib.parse
import os

env_path = "agent/.env"

def fix_env():
    if not os.path.exists(env_path):
        print("No .env found")
        return

    with open(env_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith("DATABASE_URL="):
            # Format: postgresql://user:pass@host:port/db?sslmode=require
            # Problem: pass contains @
            # We know the specific structure we generated:
            # postgresql://REDACTED_USER:REDACTED!$@thedefinitive-db...
            
            # Split by '://'
            prefix, rest = line.strip().split("://", 1)
            # rest = user:pass@host:port/db...
            
            # We want to find the host. Host starts after the LAST @ that is before the port/path?
            # Actually, standard format is user:pass@host.
            # If pass has @, we are doomed unless we know the user/host or parse diligently.
            
            # We know the user is 'REDACTED_USER'.
            user = "REDACTED_USER"
            
            # Find user in rest
            if rest.startswith(user + ":"):
                # rest = REDACTED_USER:PASSWORD@HOST...
                # Remove user:
                rest_no_user = rest[len(user)+1:]
                # rest_no_user = PASSWORD@HOST...
                
                # We need to find where Password ends and Host starts.
                # We know Host starts with 'REDACTED_SERVER_'
                # Let's split by '@REDACTED_SERVER_'
                parts = rest_no_user.split("@REDACTED_SERVER_")
                
                if len(parts) >= 2:
                    # Password is the first part (re-join if somehow split multiple times, but host pattern is unique enough)
                    password = parts[0]
                    host_part = "REDACTED_SERVER_" + parts[1]
                    
                    # Encode password
                    encoded_pass = urllib.parse.quote_plus(password)
                    
                    new_url = f"{prefix}://{user}:{encoded_pass}@{host_part}"
                    new_lines.append(f"DATABASE_URL={new_url}\n")
                    print(f"Fixed URL: {new_url}")
                else:
                     new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(env_path, "w") as f:
        f.writelines(new_lines)
    print("Updated .env")

if __name__ == "__main__":
    fix_env()
