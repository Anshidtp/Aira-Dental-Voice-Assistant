from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from backend.config.settings import settings
from backend.database.connect import Database
from backend.api.routes import appointments, voice, webhooks


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(
    settings.LOG_FILE,
    rotation=settings.LOG_ROTATION,
    retention="30 days",
    compression="zip",
    level=settings.LOG_LEVEL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Dental Voice AI Application...")
    
    # Connect to MongoDB
    await Database.connect_db()
    logger.info("MongoDB connection established")
    
    logger.info(f"Application running in {settings.ENVIRONMENT} mode")
    logger.info(f"Database: {settings.MONGODB_DB_NAME}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Dental Voice AI Application...")
    await Database.close_db()
    logger.info("MongoDB connection closed")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multilingual Voice AI Chatbot for Dental Clinic with MongoDB",
    lifespan=lifespan,
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Include routers
app.include_router(
    voice.router,
    prefix="/api/voice",
    tags=["Voice & LiveKit"]
)

app.include_router(
    appointments.router,
    prefix="/api/appointments",
    tags=["Appointments"]
)

app.include_router(
    webhooks.router,
    prefix="/api/webhooks",
    tags=["Webhooks"]
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "MongoDB",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    try:
        # Check MongoDB connection
        db_client = Database.client
        if db_client:
            await db_client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "livekit": "configured",
        "groq": "configured",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )