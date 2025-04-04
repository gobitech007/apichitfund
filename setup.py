#!/usr/bin/env python
"""
Setup script for installing dependencies and preparing the environment.
"""

import os
import sys
import subprocess
import argparse

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Setup the application environment")
    parser.add_argument(
        "--with-debug", 
        action="store_true",
        help="Install debugging tools"
    )
    return parser.parse_args()

def install_dependencies(with_debug=False):
    """Install dependencies using pip"""
    print("📦 Installing dependencies...")
    
    # Install core dependencies
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Install debugging tools if requested
    if with_debug:
        print("🔧 Installing debugging tools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "debugpy"])
    
    print("✅ Dependencies installed successfully!")

def main():
    """Main entry point"""
    args = parse_args()
    
    print("=" * 50)
    print("MyChitFund API Setup")
    print("=" * 50)
    
    install_dependencies(with_debug=args.with_debug)
    
    print("\n🚀 Setup complete! You can now run the application:")
    print("  Development mode: python run.py --mode dev")
    print("  Debug mode:       python run.py --mode debug")
    print("  Production mode:  python run.py --mode prod")

if __name__ == "__main__":
    main()