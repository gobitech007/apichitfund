#!/usr/bin/env python3
"""
Simple monitoring script for MyChitFund API cluster
"""
import psutil
import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, List

class APIMonitor:
    """Monitor API cluster health and performance"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.health_url = f"{api_url}/health"
        self.ready_url = f"{api_url}/ready"
        
    def check_health(self) -> Dict:
        """Check API health status"""
        try:
            response = requests.get(self.health_url, timeout=5)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None
            }
    
    def check_readiness(self) -> Dict:
        """Check API readiness status"""
        try:
            response = requests.get(self.ready_url, timeout=5)
            return {
                "status": "ready" if response.status_code == 200 else "not_ready",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None
            }
    
    def get_system_stats(self) -> Dict:
        """Get system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    def get_process_stats(self) -> List[Dict]:
        """Get stats for API-related processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
            try:
                if any(keyword in ' '.join(proc.info['cmdline'] or []) 
                      for keyword in ['gunicorn', 'uvicorn', 'app:app']):
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent'],
                        "cmdline": ' '.join(proc.info['cmdline'] or [])
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def monitor_once(self) -> Dict:
        """Perform one monitoring check"""
        timestamp = datetime.now().isoformat()
        
        health = self.check_health()
        readiness = self.check_readiness()
        system = self.get_system_stats()
        processes = self.get_process_stats()
        
        return {
            "timestamp": timestamp,
            "health": health,
            "readiness": readiness,
            "system": system,
            "processes": processes,
            "process_count": len(processes)
        }
    
    def monitor_continuous(self, interval: int = 30, duration: int = None):
        """Monitor continuously"""
        print(f"🔍 Starting continuous monitoring (interval: {interval}s)")
        print(f"API URL: {self.api_url}")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            while True:
                stats = self.monitor_once()
                self.print_stats(stats)
                
                # Check if duration limit reached
                if duration and (time.time() - start_time) >= duration:
                    print(f"\n⏰ Monitoring duration ({duration}s) reached. Stopping.")
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
    
    def print_stats(self, stats: Dict):
        """Print monitoring stats in a readable format"""
        timestamp = stats['timestamp']
        health = stats['health']
        readiness = stats['readiness']
        system = stats['system']
        processes = stats['processes']
        
        print(f"\n📊 {timestamp}")
        print("-" * 40)
        
        # Health status
        health_icon = "✅" if health['status'] == "healthy" else "❌"
        print(f"{health_icon} Health: {health['status']}")
        if health.get('response_time'):
            print(f"   Response time: {health['response_time']:.3f}s")
        if health.get('error'):
            print(f"   Error: {health['error']}")
        
        # Readiness status
        ready_icon = "✅" if readiness['status'] == "ready" else "❌"
        print(f"{ready_icon} Readiness: {readiness['status']}")
        if readiness.get('response_time'):
            print(f"   Response time: {readiness['response_time']:.3f}s")
        
        # System resources
        print(f"💻 System:")
        print(f"   CPU: {system['cpu_percent']:.1f}%")
        print(f"   Memory: {system['memory_percent']:.1f}%")
        print(f"   Disk: {system['disk_percent']:.1f}%")
        if system.get('load_average'):
            print(f"   Load: {system['load_average']}")
        
        # Process information
        print(f"⚙️  Processes: {len(processes)}")
        for proc in processes:
            print(f"   PID {proc['pid']}: {proc['name']} "
                  f"(CPU: {proc['cpu_percent']:.1f}%, "
                  f"Memory: {proc['memory_percent']:.1f}%)")

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MyChitFund API Cluster Monitor")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="API base URL")
    parser.add_argument("--interval", type=int, default=30, 
                       help="Monitoring interval in seconds")
    parser.add_argument("--duration", type=int, 
                       help="Monitoring duration in seconds (default: infinite)")
    parser.add_argument("--once", action="store_true", 
                       help="Run monitoring check once and exit")
    parser.add_argument("--json", action="store_true", 
                       help="Output in JSON format")
    
    args = parser.parse_args()
    
    monitor = APIMonitor(args.url)
    
    if args.once:
        # Single check
        stats = monitor.monitor_once()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            monitor.print_stats(stats)
    else:
        # Continuous monitoring
        monitor.monitor_continuous(args.interval, args.duration)

if __name__ == "__main__":
    # Install required package if not available
    try:
        import psutil
        import requests
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Install with: pip install psutil requests")
        sys.exit(1)
    
    main()