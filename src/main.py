"""
theCouncil API main application entry point.
"""
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.application.automation_registry.registry import AutomationRegistry
from src.application.automation_manager import AutomationManager
from src.interfaces.api.router_manager import RouterManager
from src.interfaces.console.router import router as console_router
from src.shared.exceptions import TheCouncilError
from src.shared.config import get_settings
from src.shared.logging import setup_logging
# Importar directamente el router de GeoPark
from src.interfaces.api.geopark_automation_collect.handlers import router as geopark_router

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="theCouncil API",
    description="Dynamic API system for GPT integration",
    version="0.1.0",
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create automation registry and manager - make them global
automation_registry = AutomationRegistry()
automation_manager = AutomationManager(app, automation_registry)

# Export registry for dependency injection
def get_automation_registry():
    """Return the global automation registry."""
    return automation_registry

# Initialize router manager (use the one created by automation_manager)
router_manager = automation_manager.router_manager

# Include the console router for automation management
app.include_router(console_router, prefix="/console", tags=["Console"])

# Include the GeoPark router directly
app.include_router(geopark_router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting theCouncil API")
    
    # Initialize the automation manager which will load automations and register routes
    await automation_manager.initialize()
    
    # Store router_manager in app.state for middleware to access
    app.state.router_manager = router_manager
    logger.info("Router manager stored in app state for middleware access")
    
    # Log that GeoPark router has been included directly
    logger.info(f"GeoPark router included directly with routes: {[route.path for route in geopark_router.routes]}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down theCouncil API")
    # Perform any cleanup tasks here


@app.middleware("http")
async def handle_deleted_automations(request: Request, call_next):
    """Middleware to handle requests to deleted automation endpoints."""
    # Only check API requests, not console or other routes
    if request.url.path.startswith("/api/"):
        # This is a safe way to access router_manager via app.state
        # which is set during startup
        if hasattr(app.state, "router_manager") and \
           app.state.router_manager.is_deleted_automation_path(request.url.path):
            logger.info(f"Caught request to deleted automation path: {request.url.path}")
            return JSONResponse(
                status_code=404,
                content={"detail": "This automation endpoint has been deleted."},
            )
    return await call_next(request)

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
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": exc.__class__.__name__},
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def get_root():
    # Get count of active automations
    automations = await automation_registry.get_all_automations()
    active_count = sum(1 for a in automations if a.status == "active")
    
    return {
        "message": "Welcome to theCouncil API",
        "version": "0.1.0",
        "active_automations": active_count,
        "total_automations": len(automations)
    }


# Console router is already included above

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
