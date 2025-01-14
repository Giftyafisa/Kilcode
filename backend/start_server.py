import subprocess
import sys
import os
import logging
from pathlib import Path
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)

def check_port_available(port):
    """Check if the port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except:
        return False

def check_requirements():
    """Check if all required packages are installed"""
    required = [
        'fastapi', 'uvicorn', 'pyOpenSSL', 'requests', 
        'python-multipart', 'python-jose', 'passlib',
        'sqlalchemy', 'alembic', 'psycopg2-binary'
    ]
    for package in required:
        try:
            __import__(package)
            logging.info(f"Package {package} is installed")
        except ImportError:
            logging.info(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    try:
        # Check if port 8000 is available
        if not check_port_available(8000):
            logging.error("Port 8000 is already in use!")
            sys.exit(1)

        # Check and install requirements
        check_requirements()
        
        # Generate SSL certificates if they don't exist
        if not Path("fullchain.pem").exists() or not Path("privkey.pem").exists():
            logging.info("Generating SSL certificates...")
            subprocess.run([sys.executable, "generate_ssl.py"], check=True)
        
        # Start DuckDNS updater in background
        logging.info("Starting DuckDNS updater...")
        duckdns_process = subprocess.Popen(
            [sys.executable, "update_duckdns.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit to ensure DuckDNS is updated
        logging.info("Waiting for initial DuckDNS update...")
        subprocess.run("timeout 10", shell=True)
        
        try:
            # Start the main server
            logging.info("Starting main server...")
            server_process = subprocess.run(
                [sys.executable, "main.py"],
                check=True
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"Server failed to start: {str(e)}")
            raise
        finally:
            # Clean up DuckDNS updater process
            logging.info("Shutting down DuckDNS updater...")
            duckdns_process.terminate()
            try:
                duckdns_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                duckdns_process.kill()

    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 