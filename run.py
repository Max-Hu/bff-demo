#!/usr/bin/env python3
"""
CI/CD Scan API Server Startup Script
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import settings


def main():
    """Main startup function"""
    print("🚀 Starting CI/CD Scan API Server...")
    print(f"📡 Server: {settings.host}:{settings.port}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"📊 Log level: {settings.log_level}")
    print(f"🔗 Jenkins URL: {settings.jenkins_url}")
    print(f"🗄️  Database: {settings.oracle_host}:{settings.oracle_port}/{settings.oracle_service}")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main() 