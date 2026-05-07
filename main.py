"""
AI Reception System API
FastAPI application with Swagger documentation and Supabase integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with custom OpenAPI configuration
app = FastAPI(
    title="AI Reception System API",
    description="API for managing AI-powered reception calls, appointments, and business interactions",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",  # OpenAPI schema
)

# Configure CORS - Allow all origins for this session
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Reception System API",
        version="1.0.0",
        description="Complete AI reception system with call management, appointments, and analytics",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Reception System",
        "version": "1.0.0"
    }

# API Routes placeholder
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to AI Reception System API",
        "docs": "/docs",
        "schema": "/openapi.json"
    }

from routers import all_routers

# Include all routers from the routers package
for router in all_routers:
    app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    environment = os.getenv("ENVIRONMENT", "development")
    
    logger.info(f"Starting AI Reception API on {host}:{port} ({environment})")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=(environment == "development"),
        log_level="info"
    )
