import socket
import requests
import time
from contextlib import closing

def check_port(port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(2)
        try:
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                print(f"✓ Port {port} is open")
                return True
            else:
                print(f"✗ Port {port} is closed")
                return False
        except socket.error as e:
            print(f"Error checking port {port}: {e}")
            return False

def check_external_ip():
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            ip = response.text
            print(f"✓ External IP: {ip}")
            return ip
    except Exception as e:
        print(f"✗ Could not get external IP: {e}")
    return None

if __name__ == "__main__":
    print("\n=== Testing Server Connection ===\n")
    
    # Check if port 8000 is open
    port_open = check_port(8000)
    
    # Get external IP
    external_ip = check_external_ip()
    
    if port_open and external_ip:
        print("\nAll checks passed! Your server should be accessible.")
        print(f"Try accessing: http://{external_ip}:8000")
    else:
        print("\nSome checks failed. Please ensure:")
        print("1. The server is running")
        print("2. No other application is using port 8000")
        print("3. Your firewall rules are correctly configured")
        print("4. Your router has port 8000 forwarded to this machine") 