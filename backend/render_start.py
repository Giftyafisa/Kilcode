import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor

def run_server(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command {command}: {e}")
        sys.exit(1)

def main():
    # Get the port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Define commands for each server
    commands = [
        f"uvicorn app.main:app --host 0.0.0.0 --port {port}",
        f"uvicorn app.admin_server:app --host 0.0.0.0 --port {port + 1}",
        f"python payment_admin_server.py --port {port + 2}",
        f"python code_analyzer_server.py --port {port + 3}"
    ]

    # Run all servers in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(run_server, commands)

if __name__ == "__main__":
    main() 