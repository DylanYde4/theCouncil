"""
Vercel API entrypoint for theCouncil project.
This module adapts the FastAPI application to run on Vercel's serverless environment.
"""
import sys
import os
import logging
from contextlib import asynccontextmanager

# Mark environment as serverless
os.environ['VERCEL'] = '1'

# Add project root to path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary components
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.application.automation_registry.registry import AutomationRegistry
from src.application.automation_manager import AutomationManager
from src.interfaces.console.router import router as console_router
from src.shared.exceptions import TheCouncilError
from src.shared.config import get_settings
from src.shared.logging import setup_logging

# Set up logging (will detect serverless environment)
setup_logging()
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Create global instances
automation_registry = AutomationRegistry()
automation_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize components on startup
    logger.info("Starting theCouncil API (Vercel serverless mode)")
    global automation_manager
    
    # Create automation manager
    automation_manager = AutomationManager(app, automation_registry)
    
    # Initialize the automation manager
    await automation_manager.initialize()
    
    # Store router_manager in app.state for middleware to access
    app.state.router_manager = automation_manager.router_manager
    logger.info("Router manager stored in app state for middleware access")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down theCouncil API")

# Create FastAPI application with lifespan manager for proper initialization
app = FastAPI(
    title="theCouncil API",
    description="Dynamic API system for GPT integration",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the console router for automation management
app.include_router(console_router, prefix="/console", tags=["Console"])

# Middleware to handle deleted automations
@app.middleware("http")
async def handle_deleted_automations(request: Request, call_next):
    """Middleware to handle requests to deleted automation endpoints."""
    # Only check API requests, not console or other routes
    if request.url.path.startswith("/api/"):
        # This is a safe way to access router_manager via app.state
        if hasattr(app.state, "router_manager") and \
           app.state.router_manager.is_deleted_automation_path(request.url.path):
            logger.info(f"Caught request to deleted automation path: {request.url.path}")
            return JSONResponse(
                status_code=404,
                content={"detail": "This automation endpoint has been deleted."},
            )
    return await call_next(request)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )

@app.exception_handler(TheCouncilError)
async def thecouncil_exception_handler(request: Request, exc: TheCouncilError):
    """Handle TheCouncilError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc), "type": exc.error_type},
    )

@app.get("/")
async def get_root():
    """API root endpoint."""
    return {
        "name": "theCouncil API",
        "version": "0.1.0",
        "description": "Dynamic API system for GPT integration",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Central health check endpoint for the entire API.
    
    Returns status information about the API and its components.
    """
    # Get all registered automations from the registry
    automations = []
    if automation_registry and hasattr(automation_registry, 'get_all_automations'):
        try:
            automations = automation_registry.get_all_automations()
        except Exception as e:
            logger.error(f"Error getting automations: {e}")
    
    return {
        "status": "healthy",
        "timestamp": str(settings.current_time),
        "version": "0.1.0",
        "environment": "serverless" if settings.is_serverless else "local",
        "registered_automations": len(automations) if automations else 0,
        "automations": [a.id for a in automations] if automations else []
    }
