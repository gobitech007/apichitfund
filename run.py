#!/usr/bin/env python
"""
Run script for the FastAPI application.
This script provides different run modes for the application.
"""

import os
import sys
import argparse
import uvicorn

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run the FastAPI application")
    parser.add_argument(
        "--mode", 
        type=str, 
        default="dev",
        choices=["dev", "debug", "prod"],
        help="Run mode: dev, debug, or prod"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind the server to"
    )
    return parser.parse_args()

def run_dev_mode(host, port):
    """Run the application in development mode"""
    print(f"🚀 Starting server in DEVELOPMENT mode on http://{host}:{port}")
    print(f"📚 API documentation available at http://localhost:{port}/api/docs")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

def run_debug_mode(host, port):
    """Run the application in debug mode"""
    print(f"🔍 Starting server in DEBUG mode on http://{host}:{port}")
    print(f"📚 API documentation available at http://localhost:{port}/api/docs")

    try:
        # Import and run the debug script
        import debug
        debug.run_app_with_debugger()
    except ImportError:
        print("❌ Debug module not found. Running in fallback debug mode.")
        # Fallback to a simple debug configuration
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="debug"
        )

def run_prod_mode(host, port):
    """Run the application in production mode"""
    print(f"🚀 Starting server in PRODUCTION mode on http://{host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        workers=4,
        log_level="warning"
    )

def main():
    """Main entry point"""
    args = parse_args()
    
    # Print run information
    print("=" * 50)
    print(f"MyChitFund API Server")
    print("=" * 50)
    
    # Run in the specified mode
    if args.mode == "dev":
        run_dev_mode(args.host, args.port)
    elif args.mode == "debug":
        run_debug_mode(args.host, args.port)
    elif args.mode == "prod":
        run_prod_mode(args.host, args.port)
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()