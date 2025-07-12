import subprocess
import sys
import os
import time
import signal
import requests
from dotenv import load_dotenv
import psutil
import webbrowser
from pathlib import Path

# Configuration
MONGODB_URI = "mongodb://localhost:27017/github_events"
FLASK_PORT = 5000
REACT_PORT = 3000
NGROK_DOMAIN = "safe-proper-muskox.ngrok-free.app"
NGROK_AUTH_TOKEN = "2zm2trRBl9BhevZqX1VMuQlDdw_35aKHA3A7EHhz2sdHyNfo"

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        print(f"Killing process {proc.name()} (PID: {proc.pid}) on port {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"Error killing process on port {port}: {e}")

def create_env_file():
    """Create .env file with configuration"""
    env_content = f"""MONGO_URI={MONGODB_URI}
FLASK_ENV=development
"""
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Created .env file")

def create_ngrok_config():
    """Create ngrok configuration file"""
    config_content = f"""version: "2"
authtoken: {NGROK_AUTH_TOKEN}
tunnels:
  webhook:
    proto: http
    addr: {FLASK_PORT}
    domain: {NGROK_DOMAIN}
"""
    with open('ngrok.yml', 'w') as f:
        f.write(config_content)
    print("✅ Created ngrok configuration")

def wait_for_service(url, service_name, timeout=30):
    """Wait for a service to become available"""
    print(f"Waiting for {service_name} to start...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ {service_name} is running")
                return True
        except requests.exceptions.RequestException:
            time.sleep(1)
    print(f"❌ {service_name} failed to start")
    return False

def start_flask():
    """Start Flask backend"""
    print("\n=== Starting Flask Backend ===")
    kill_process_on_port(FLASK_PORT)
    
    flask_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if wait_for_service(f"http://localhost:{FLASK_PORT}/health", "Flask backend"):
        return flask_process
    return None

def start_react():
    """Start React frontend"""
    print("\n=== Starting React Frontend ===")
    kill_process_on_port(REACT_PORT)
    
    os.chdir('frontend')
    npm_install_process = subprocess.run(
        ["npm", "install"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if npm_install_process.returncode != 0:
        print("❌ Failed to install npm dependencies")
        return None
        
    react_process = subprocess.Popen(
        ["npm", "start"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    os.chdir('..')
    
    if wait_for_service(f"http://localhost:{REACT_PORT}", "React frontend"):
        return react_process
    return None

def start_ngrok():
    """Start ngrok tunnel"""
    print("\n=== Starting ngrok ===")
    create_ngrok_config()
    
    ngrok_process = subprocess.Popen(
        ["ngrok", "start", "--config", "ngrok.yml", "webhook"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for ngrok to start
    time.sleep(3)
    try:
        response = requests.get(f"https://{NGROK_DOMAIN}/health")
        if response.status_code == 200:
            print("✅ ngrok tunnel is running")
            return ngrok_process
    except:
        print("❌ Failed to start ngrok tunnel")
        return None

def cleanup(processes):
    """Clean up all running processes"""
    print("\nShutting down services...")
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
    
    # Kill any remaining processes on our ports
    kill_process_on_port(FLASK_PORT)
    kill_process_on_port(REACT_PORT)

def main():
    # Store process handles for cleanup
    processes = []
    
    try:
        # Create necessary configuration files
        create_env_file()
        
        # Start services
        flask_process = start_flask()
        if not flask_process:
            return
        processes.append(flask_process)
        
        react_process = start_react()
        if not react_process:
            cleanup(processes)
            return
        processes.append(react_process)
        
        ngrok_process = start_ngrok()
        if not ngrok_process:
            cleanup(processes)
            return
        processes.append(ngrok_process)
        
        # Open browser tabs
        webbrowser.open(f"http://localhost:{REACT_PORT}")
        
        print("\n=== All Services Started Successfully! ===")
        print(f"\n🌐 Frontend URL: http://localhost:{REACT_PORT}")
        print(f"🔧 Backend URL: http://localhost:{FLASK_PORT}")
        print(f"📡 Webhook URL: https://{NGROK_DOMAIN}/webhook")
        print("\nGitHub Webhook Configuration:")
        print("1. Go to your repository settings")
        print("2. Click on 'Webhooks' → 'Add webhook'")
        print(f"3. Set Payload URL to: https://{NGROK_DOMAIN}/webhook")
        print("4. Set Content type to: application/json")
        print("5. Select events: Pushes, Pull requests, Pull request reviews")
        print("\nPress Ctrl+C to stop all services...")
        
        # Keep the script running and monitor processes
        while True:
            if any(p.poll() is not None for p in processes if p):
                print("\nOne of the services has stopped unexpectedly!")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    finally:
        cleanup(processes)
        print("All services have been stopped.")

if __name__ == "__main__":
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add psutil to requirements.txt if not present
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    if 'psutil' not in requirements:
        with open('requirements.txt', 'a') as f:
            f.write('\npsutil==5.9.8\n')
    
    main() 