"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import measurements
from app.core.config import settings
import os

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Body measurement extraction from photos using computer vision"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(
    measurements.router,
    prefix="/api/measurements",
    tags=["measurements"]
)

# Import size recommendations router
from app.api.routes import size_recommendations

app.include_router(
    size_recommendations.router,
    prefix="/api/size-recommendations",
    tags=["size-recommendations"]
)


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse("templates/index.html")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    print(f"🚀 {settings.app_name} v{settings.app_version} started")
    print(f"📸 MediaPipe model complexity: {settings.mediapipe_model_complexity}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Shutting down gracefully")
