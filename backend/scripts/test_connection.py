import requests
import websockets
import asyncio
import sys
import json
import ssl
import socket
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def check_port_open(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"Port {port} is open on {host}")
            return True
        else:
            print(f"Port {port} is closed on {host}")
            return False
    except Exception as e:
        print(f"Error checking port {port}: {str(e)}")
        return False
    finally:
        sock.close()

def test_http_connection(url):
    try:
        print(f"\nTesting HTTP connection to {url}")
        print("Connection details:")
        parsed_url = requests.utils.urlparse(url)
        print(f"Host: {parsed_url.hostname}")
        print(f"Port: {parsed_url.port or 443}")
        print(f"Path: {parsed_url.path}")
        
        # First check if port is open
        port_open = check_port_open(parsed_url.hostname, parsed_url.port or 443)
        if not port_open:
            print("Port is closed - connection cannot be established")
            return False
            
        response = requests.get(
            url,
            verify=False,
            timeout=5,
            headers={'User-Agent': 'KilcodeTestScript/1.0'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:200]}...")  # First 200 chars
        print("Success: ✓")
        return True
    except requests.exceptions.SSLError as e:
        print(f"SSL Error: {str(e)}")
        print("Failed: ✗")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {str(e)}")
        print("Failed: ✗")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Failed: ✗")
        return False

async def test_websocket_connection(url):
    try:
        print(f"\nTesting WebSocket connection to {url}")
        print("Connection details:")
        parsed_url = requests.utils.urlparse(url)
        print(f"Host: {parsed_url.hostname}")
        print(f"Port: {parsed_url.port or 443}")
        
        # First check if port is open
        port_open = check_port_open(parsed_url.hostname, parsed_url.port or 443)
        if not port_open:
            print("Port is closed - connection cannot be established")
            return False
            
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with websockets.connect(
            url,
            ssl=ssl_context,
            ping_interval=None,
            ping_timeout=None,
            close_timeout=5
        ) as websocket:
            print("WebSocket connected")
            message = {
                "type": "ping",
                "timestamp": str(datetime.now()),
                "client": "test_script"
            }
            await websocket.send(json.dumps(message))
            print("Ping sent")
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Response received: {response}")
                print("Success: ✓")
                return True
            except asyncio.TimeoutError:
                print("Timeout waiting for response")
                print("Failed: ✗")
                return False
                
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"Invalid status code: {str(e)}")
        print("Failed: ✗")
        return False
    except websockets.exceptions.InvalidMessage as e:
        print(f"Invalid message: {str(e)}")
        print("Failed: ✗")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Failed: ✗")
        return False

async def main():
    host = "192.168.43.91"
    port = 8000
    
    print(f"Starting connection tests to {host}:{port}")
    print("=" * 50)
    
    # Test basic port connectivity first
    print("\nTesting basic connectivity:")
    if not check_port_open(host, port):
        print("\nCritical Error: Cannot establish basic connection to server")
        print("Please check:")
        print("1. Server is running")
        print("2. Firewall settings")
        print("3. Network connectivity")
        return
    
    # Test HTTP endpoints
    endpoints = [
        f"https://{host}:{port}/health",
        f"https://{host}:{port}/api/v1/marketplace/status",
    ]
    
    ws_endpoints = [
        f"wss://{host}:{port}"
    ]
    
    http_results = []
    print("\nTesting HTTP endpoints:")
    for url in endpoints:
        result = test_http_connection(url)
        http_results.append(result)
    
    ws_results = []
    print("\nTesting WebSocket endpoints:")
    for url in ws_endpoints:
        result = await test_websocket_connection(url)
        ws_results.append(result)
    
    total_tests = len(http_results) + len(ws_results)
    successful_tests = sum(http_results) + sum(ws_results)
    
    print("\nTest Summary:")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    
    if successful_tests < total_tests:
        print("\nTroubleshooting Tips:")
        print("1. Check if the server is running with SSL enabled")
        print("2. Verify the firewall allows both HTTP and WebSocket traffic")
        print("3. Ensure the SSL certificates are properly configured")
        print("4. Check if the server is listening on all network interfaces")

if __name__ == "__main__":
    print("Connection Test Script v1.1")
    print("==========================")
    asyncio.run(main()) 