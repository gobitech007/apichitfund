#!/usr/bin/env python
"""
Debug script for running the FastAPI application with enhanced debugging.
This script sets up debugging configuration and runs the application
with verbose logging and auto-reloading.
"""

import os
import sys
import logging
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("debug")

def setup_debug_tools():
    """Set up additional debugging tools if available"""
    try:
        # Try to import debugpy for remote debugging
        import debugpy
        logger.info("🔧 debugpy is available for remote debugging")

        # Uncomment these lines to enable remote debugging with VS Code
        # debugpy.listen(("0.0.0.0", 5678))
        # logger.info("⏳ Waiting for debugger attach at 0.0.0.0:5678")
        # debugpy.wait_for_client()
        # logger.info("🔗 Debugger attached!")
    except ImportError:
        logger.info("ℹ️ debugpy not available. Install with: pip install debugpy")
        pass

def run_app_with_debugger():
    """Run the FastAPI application with debugging enabled"""
    logger.info("🚀 Starting application in DEBUG mode")

    # Print environment information
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📂 Working directory: {os.getcwd()}")

    # Enable SQLAlchemy logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # Run the application with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_delay=0.25,
        log_level="debug",
        access_log=True,
        use_colors=True
    )

def print_debug_info():
    """Print debugging information about the environment"""
    logger.info("=" * 50)
    logger.info("🔍 DEBUG INFORMATION")
    logger.info("=" * 50)

    # Python info
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📂 Working directory: {os.getcwd()}")

    # Installed packages
    try:
        import pkg_resources
        logger.info("📦 Installed packages:")
        for pkg in pkg_resources.working_set:
            logger.info(f"   - {pkg.project_name} {pkg.version}")
    except ImportError:
        logger.info("❌ Could not retrieve package information")

    logger.info("=" * 50)

if __name__ == "__main__":
    try:
        setup_debug_tools()
        print_debug_info()
        run_app_with_debugger()
    except Exception as e:
        logger.exception(f"❌ Error running application: {e}")
        sys.exit(1)