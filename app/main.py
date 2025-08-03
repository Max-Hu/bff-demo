import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings

# Configure logging FIRST, before importing other modules
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
        logging.FileHandler('/app/logs/app.log')  # File handler
    ]
)

# Set specific logger levels
logging.getLogger('app').setLevel(getattr(logging, settings.log_level))
logging.getLogger('app.jenkins_client').setLevel(getattr(logging, settings.log_level))

logger = logging.getLogger(__name__)

# Import other modules after logging is configured
from .routers import scan
from .database import db_manager
from .jenkins_client import jenkins_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CI/CD Scan API Server...")
    
    # Test database connection
    try:
        logger.info("Testing database connection...")
        # Database connection is established in DatabaseManager.__init__
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Don't fail startup, but log the error
    
    # Test Jenkins connection
    try:
        logger.info("Testing Jenkins connection...")
        if jenkins_client.test_connection():
            logger.info("Jenkins connection successful")
        else:
            logger.warning("Jenkins connection failed")
    except Exception as e:
        logger.error(f"Jenkins connection test failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CI/CD Scan API Server...")
    db_manager.close()


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(scan.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CI/CD Scan API Server",
        "version": settings.api_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "version": settings.api_version,
        "database": "unknown",
        "jenkins": "unknown"
    }
    
    # Check database
    try:
        # Simple database check
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Jenkins
    try:
        if jenkins_client.test_connection():
            health_status["jenkins"] = "connected"
        else:
            health_status["jenkins"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["jenkins"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 