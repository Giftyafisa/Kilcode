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
    port = int(os.environ.get("PORT", 8000))
    
    # Run only the main server as Render expects a single service
    command = f"python -m uvicorn app.main:app --host 0.0.0.0 --port {port}"
    run_server(command)

if __name__ == "__main__":
    main() 