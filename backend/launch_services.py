import subprocess 
import threading 
import sys 
import os 
ECHO is off.
def run_service(command, cwd): 
    try: 
        process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=sys.stdout, stderr=sys.stderr) 
        process.wait() 
    except Exception as e: 
        print(f"Error running service: {e}") 
ECHO is off.
def main(): 
    services = [ 
        {"command": "uvicorn app.main:app --reload --port 8000", "cwd": "backend"}, 
        {"command": "python -m uvicorn app.admin_server:app --reload --port 8001", "cwd": "backend"}, 
        {"command": "python payment_admin_server.py", "cwd": "backend"}, 
        {"command": "python code_analyzer_server.py", "cwd": "backend"}, 
        {"command": "npm run dev", "cwd": "frontend"}, 
        {"command": "npm run dev", "cwd": "admin"}, 
        {"command": "npm run start:analyzer", "cwd": "admin"} 
    ] 
ECHO is off.
    threads = [] 
    for service in services: 
        thread = threading.Thread(target=run_service, args=(service['command'], service['cwd'])) 
        thread.start() 
        threads.append(thread) 
ECHO is off.
    for thread in threads: 
        thread.join() 
ECHO is off.
if __name__ == "__main__": 
    main() 
