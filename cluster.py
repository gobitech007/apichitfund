"""
Cluster management script for MyChitFund API
Supports multiple deployment modes: development, production, and custom worker configurations
"""
import os
import sys
import argparse
import multiprocessing
import subprocess
import signal
import time
from typing import List, Optional

class ClusterManager:
    """Manages FastAPI application clusters"""
    
    def __init__(self):
        self.workers: List[subprocess.Popen] = []
        self.master_pid = os.getpid()
        
    def get_worker_count(self, mode: str = "auto") -> int:
        """Calculate optimal worker count based on mode"""
        cpu_count = multiprocessing.cpu_count()
        
        if mode == "auto":
            # Recommended: (2 x CPU cores) + 1
            return (cpu_count * 2) + 1
        elif mode == "cpu":
            # One worker per CPU core
            return cpu_count
        elif mode == "light":
            # Minimal workers for development
            return 2
        elif mode == "heavy":
            # Maximum workers for high load
            return cpu_count * 4
        else:
            try:
                return int(mode)
            except ValueError:
                print(f"Invalid worker count: {mode}. Using auto mode.")
                return (cpu_count * 2) + 1
    
    def start_uvicorn_cluster(self, workers: int, host: str = "0.0.0.0", port: int = 8000):
        """Start multiple Uvicorn workers manually"""
        print(f"Starting {workers} Uvicorn workers on {host}:{port}")
        
        # Start workers on different ports
        base_port = port
        for i in range(workers):
            worker_port = base_port + i
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app:app",
                "--host", host,
                "--port", str(worker_port),
                "--worker-class", "uvicorn.workers.UvicornWorker",
                "--access-log",
                "--log-level", "info"
            ]
            
            print(f"Starting worker {i+1} on port {worker_port}")
            process = subprocess.Popen(cmd)
            self.workers.append(process)
            time.sleep(1)  # Stagger startup
        
        print(f"All {workers} workers started successfully!")
        print("Workers running on ports:", [base_port + i for i in range(workers)])
        
    def start_gunicorn_cluster(self, workers: Optional[int] = None, host: str = "0.0.0.0", port: int = 8000):
        """Start Gunicorn with Uvicorn workers"""
        if workers is None:
            workers = self.get_worker_count("auto")
            
        print(f"Starting Gunicorn with {workers} Uvicorn workers on {host}:{port}")
        
        cmd = [
            "gunicorn",
            "app:app",
            "-c", "gunicorn.conf.py",
            "--workers", str(workers),
            "--worker-class", "uvicorn.workers.UvicornWorker",
            "--bind", f"{host}:{port}",
            "--preload"
        ]
        
        try:
            process = subprocess.Popen(cmd)
            self.workers.append(process)
            print(f"Gunicorn master process started with PID: {process.pid}")
            return process
        except FileNotFoundError:
            print("Gunicorn not found. Please install it: pip install gunicorn")
            return None
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}. Shutting down workers...")
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self):
        """Shutdown all workers gracefully"""
        print("Shutting down all workers...")
        for process in self.workers:
            if process.poll() is None:  # Process is still running
                print(f"Terminating worker PID: {process.pid}")
                process.terminate()
                
        # Wait for graceful shutdown
        time.sleep(2)
        
        # Force kill if necessary
        for process in self.workers:
            if process.poll() is None:
                print(f"Force killing worker PID: {process.pid}")
                process.kill()
        
        print("All workers shut down.")
    
    def monitor_workers(self):
        """Monitor worker processes and restart if needed"""
        print("Monitoring workers... Press Ctrl+C to stop")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            while True:
                # Check if any workers have died
                for i, process in enumerate(self.workers):
                    if process.poll() is not None:
                        print(f"Worker {i+1} (PID: {process.pid}) has died. Exit code: {process.returncode}")
                        # You could implement restart logic here
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
            self.shutdown()

def main():
    parser = argparse.ArgumentParser(description="MyChitFund API Cluster Manager")
    parser.add_argument("--mode", choices=["dev", "prod", "uvicorn", "gunicorn"], 
                       default="dev", help="Deployment mode")
    parser.add_argument("--workers", default="auto", 
                       help="Number of workers (auto, cpu, light, heavy, or number)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--monitor", action="store_true", 
                       help="Monitor workers and restart if needed")
    
    args = parser.parse_args()
    
    cluster = ClusterManager()
    worker_count = cluster.get_worker_count(args.workers)
    
    print(f"MyChitFund API Cluster Manager")
    print(f"Mode: {args.mode}")
    print(f"Workers: {worker_count}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print("-" * 50)
    
    if args.mode == "dev":
        # Development mode - single process with reload
        print("Starting development server with auto-reload...")
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app:app",
            "--host", args.host,
            "--port", str(args.port),
            "--reload",
            "--log-level", "info"
        ]
        subprocess.run(cmd)
        
    elif args.mode == "uvicorn":
        # Multiple Uvicorn workers
        cluster.start_uvicorn_cluster(worker_count, args.host, args.port)
        if args.monitor:
            cluster.monitor_workers()
        else:
            # Wait for all workers
            for process in cluster.workers:
                process.wait()
                
    elif args.mode == "gunicorn":
        # Gunicorn with Uvicorn workers
        process = cluster.start_gunicorn_cluster(worker_count, args.host, args.port)
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\nShutdown requested")
                cluster.shutdown()
                
    elif args.mode == "prod":
        # Production mode with Gunicorn
        print("Starting production server with Gunicorn...")
        process = cluster.start_gunicorn_cluster(worker_count, args.host, args.port)
        if process:
            if args.monitor:
                cluster.monitor_workers()
            else:
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\nShutdown requested")
                    cluster.shutdown()

if __name__ == "__main__":
    main()