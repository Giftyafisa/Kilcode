import subprocess
import os
import sys

def setup_ssl():
    domain = "kilcode.duckdns.org"
    email = "your-email@example.com"  # Replace with your email
    
    # Create SSL directory
    ssl_dir = os.path.join(os.path.dirname(__file__), "ssl")
    os.makedirs(ssl_dir, exist_ok=True)
    
    try:
        # Get certbot path
        certbot_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", "Python312", "Scripts", "certbot.exe")
        
        # Run certbot to obtain certificates
        command = [
            certbot_path,
            "certonly",
            "--standalone",
            "--non-interactive",
            "--agree-tos",
            "--email", email,
            "-d", domain,
            "--cert-path", os.path.join(ssl_dir, "cert.pem"),
            "--key-path", os.path.join(ssl_dir, "privkey.pem"),
            "--fullchain-path", os.path.join(ssl_dir, "fullchain.pem")
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SSL certificates obtained successfully!")
            print("Certificates saved in:", ssl_dir)
        else:
            print("Error obtaining SSL certificates:")
            print(result.stderr)
            
    except Exception as e:
        print("Error:", str(e))
        sys.exit(1)

if __name__ == "__main__":
    setup_ssl() 