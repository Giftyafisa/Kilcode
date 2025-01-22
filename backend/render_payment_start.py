import subprocess
import sys
import os

def run_server(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command {command}: {e}")
        sys.exit(1)

def main():
    # Get the port from Render's environment variable
    port = int(os.environ.get("PORT", 8002))
    
    # Run the payment admin server
    command = f"python payment_admin_server.py --port {port}"
    run_server(command)

if __name__ == "__main__":
    main() 