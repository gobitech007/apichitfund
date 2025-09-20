#!/usr/bin/env python3
"""
Test script to verify clustering functionality
"""
import asyncio
import httpx
import time
import sys
from typing import List, Dict

async def test_endpoint(url: str, num_requests: int = 100) -> Dict:
    """Test an endpoint with concurrent requests"""
    print(f"Testing {url} with {num_requests} concurrent requests...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        start_time = time.time()
        
        # Create concurrent requests
        tasks = [client.get(url) for _ in range(num_requests)]
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"Error during requests: {e}")
            return {"error": str(e)}
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze responses
        successful = 0
        failed = 0
        errors = []
        
        for response in responses:
            if isinstance(response, Exception):
                failed += 1
                errors.append(str(response))
            elif hasattr(response, 'status_code') and response.status_code == 200:
                successful += 1
            else:
                failed += 1
                if hasattr(response, 'status_code'):
                    errors.append(f"HTTP {response.status_code}")
        
        return {
            "url": url,
            "total_requests": num_requests,
            "successful": successful,
            "failed": failed,
            "duration": duration,
            "requests_per_second": num_requests / duration if duration > 0 else 0,
            "success_rate": (successful / num_requests) * 100,
            "errors": errors[:5]  # Show first 5 errors
        }

async def test_cluster_performance():
    """Test cluster performance with various endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        f"{base_url}/health",
        f"{base_url}/ready", 
        f"{base_url}/api/",
    ]
    
    print("🧪 MyChitFund API Cluster Performance Test")
    print("=" * 50)
    
    results = []
    
    for endpoint in endpoints:
        try:
            result = await test_endpoint(endpoint, 50)
            results.append(result)
            
            if "error" not in result:
                print(f"✅ {endpoint}")
                print(f"   Success Rate: {result['success_rate']:.1f}%")
                print(f"   Requests/sec: {result['requests_per_second']:.1f}")
                print(f"   Duration: {result['duration']:.2f}s")
                if result['errors']:
                    print(f"   Errors: {result['errors']}")
                print()
            else:
                print(f"❌ {endpoint}: {result['error']}")
                print()
                
        except Exception as e:
            print(f"❌ {endpoint}: Failed to test - {e}")
            print()
    
    # Summary
    print("📊 Summary")
    print("-" * 30)
    total_requests = sum(r.get('total_requests', 0) for r in results if 'error' not in r)
    total_successful = sum(r.get('successful', 0) for r in results if 'error' not in r)
    avg_rps = sum(r.get('requests_per_second', 0) for r in results if 'error' not in r) / len([r for r in results if 'error' not in r]) if results else 0
    
    print(f"Total Requests: {total_requests}")
    print(f"Total Successful: {total_successful}")
    print(f"Overall Success Rate: {(total_successful/total_requests)*100:.1f}%" if total_requests > 0 else "N/A")
    print(f"Average RPS: {avg_rps:.1f}")

async def test_health_check():
    """Simple health check test"""
    print("🏥 Testing Health Check Endpoint")
    print("-" * 30)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8000/health")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Service: {data.get('service', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--health-only":
        # Quick health check only
        result = asyncio.run(test_health_check())
        sys.exit(0 if result else 1)
    else:
        # Full performance test
        print("Starting cluster performance test...")
        print("Make sure your API server is running first!")
        print("Example: python cluster.py --mode prod --workers 4")
        print()
        
        asyncio.run(test_cluster_performance())

if __name__ == "__main__":
    main()