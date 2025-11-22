#!/usr/bin/env python3
"""
Development server startup script
Single process with auto-reload for development
"""
import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("ENVIRONMENT", "development")
    
    print("🚀 Starting MyChitFund API Development Server")
    print("📍 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("⚡ Auto-reload: Enabled")
    print("-" * 50)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        reload_dirs=[".", "./payments", "./interest"],
        reload_excludes=["__pycache__", "*.pyc", ".git"]
    )