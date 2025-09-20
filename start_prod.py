#!/usr/bin/env python3
"""
Production server startup script
Multiple workers with Gunicorn for production deployment
"""
import os
import sys
import subprocess
import multiprocessing

def main():
    # Set production environment
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("ENVIRONMENT", "production")
    
    # Calculate optimal worker count
    workers = (multiprocessing.cpu_count() * 2) + 1
    
    print("🚀 Starting MyChitFund API Production Server")
    print(f"👥 Workers: {workers}")
    print("📍 Server: http://0.0.0.0:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("-" * 50)
    
    # Check if gunicorn is available
    try:
        subprocess.run(["gunicorn", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Gunicorn not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "gunicorn"], check=True)
    
    # Start Gunicorn with Uvicorn workers
    cmd = [
        "gunicorn",
        "app:app",
        "-c", "gunicorn.conf.py",
        "--workers", str(workers),
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--bind", "0.0.0.0:8000",
        "--preload"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()