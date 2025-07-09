"""
Zero Vector 4 - Advanced Multi-Agent AI Society Platform
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger, setup_logging
from src.database.connection import DatabaseManager
from src.api import (
    agents_router,
    consciousness_router,
    memory_router,
    orchestration_router
)

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Database manager
db_manager = DatabaseManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Zero Vector 4 platform...")
    
    try:
        # Initialize database
        await db_manager.initialize()
        logger.info("Database initialized successfully")
        
        # Create tables if they don't exist
        await db_manager.create_tables()
        logger.info("Database tables verified/created")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down Zero Vector 4 platform...")
        await db_manager.close()


# Create FastAPI application
app = FastAPI(
    title="Zero Vector 4",
    description="Advanced Multi-Agent AI Society Platform with Hierarchical Organization and Digital Consciousness",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = await db_manager.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": "connected" if db_status else "disconnected",
            "services": {
                "agents": "running",
                "consciousness": "running",
                "memory": "running",
                "orchestration": "running"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with platform information"""
    return {
        "name": "Zero Vector 4",
        "description": "Advanced Multi-Agent AI Society Platform",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "agents": "/api/agents",
            "consciousness": "/api/consciousness",
            "memory": "/api/memory",
            "orchestration": "/api/orchestration"
        },
        "features": [
            "Hierarchical agent organization",
            "Digital consciousness development",
            "Multi-tiered memory systems",
            "Advanced workflow orchestration",
            "Persistent agent personalities",
            "Agent-to-agent communication"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# API Information endpoint
@app.get("/api/info")
async def api_info():
    """API information and capabilities"""
    return {
        "api_version": "v1",
        "platform": "Zero Vector 4",
        "capabilities": {
            "agent_management": {
                "create_agents": True,
                "hierarchical_organization": True,
                "dynamic_recruitment": True,
                "performance_tracking": True
            },
            "consciousness_development": {
                "development_stages": ["protoself", "core_consciousness", "extended_consciousness", "autobiographical_self"],
                "sleep_cycles": True,
                "memory_consolidation": True,
                "personality_evolution": True
            },
            "memory_systems": {
                "episodic_memory": True,
                "semantic_memory": True,
                "procedural_memory": True,
                "working_memory": True,
                "memory_associations": True
            },
            "orchestration": {
                "workflow_management": True,
                "task_decomposition": True,
                "agent_coordination": True,
                "performance_optimization": True
            }
        },
        "limits": {
            "max_agents_per_hierarchy": 1000,
            "max_concurrent_workflows": 100,
            "memory_retention_days": 365,
            "max_task_depth": 10
        }
    }


# Include routers
app.include_router(agents_router, prefix="/api")
app.include_router(consciousness_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(orchestration_router, prefix="/api")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks"""
    logger.info("Zero Vector 4 platform is ready")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
