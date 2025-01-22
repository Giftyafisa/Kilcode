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
    port = int(os.environ.get("PORT", 10000))
    
    # Define commands for each server using python -m to ensure proper module resolution
    commands = [
        f"python -m uvicorn app.main:app --host 0.0.0.0 --port {port}",
        f"python -m uvicorn app.admin_server:app --host 0.0.0.0 --port {port + 1}",
        f"python payment_admin_server.py --port {port + 2}",
        f"python code_analyzer_server.py --port {port + 3}"
    ]

    # Run the main server (the first command)
    # In Render, we only need to run the main server as it assigns a single port
    run_server(commands[0])

if __name__ == "__main__":
    main() 