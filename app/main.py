"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import measurements
from app.core.config import settings
from app.core.database import mongodb
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

# Import authentication router
from app.api.routes import auth

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["authentication"]
)

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

# Import avatar generation router
from app.api.routes import avatar

app.include_router(
    avatar.router,
    prefix="/api/avatar",
    tags=["avatar"]
)

# Import virtual try-on router
from app.api.routes import tryon

app.include_router(
    tryon.router,
    prefix="/api/tryon",
    tags=["tryon"]
)

# Import fit analysis router
from app.api.routes import fit_analysis

app.include_router(
    fit_analysis.router,
    prefix="/api/fit",
    tags=["fit-analysis"]
)


@app.get("/")
async def root():
    """Serve the login/authentication page."""
    return FileResponse("templates/auth.html")


@app.get("/app")
async def app_page():
    """Serve the main application page."""
    return FileResponse("templates/index.html")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Connect to MongoDB
    await mongodb.connect_db()
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs(settings.avatar_storage_dir, exist_ok=True)
    os.makedirs(settings.avatar_assets_dir, exist_ok=True)
    os.makedirs(settings.clothing_assets_dir, exist_ok=True)
    print(f"🚀 {settings.app_name} v{settings.app_version} started")
    print(f"📸 MediaPipe model complexity: {settings.mediapipe_model_complexity}")
    print(f"👤 Avatar system enabled")
    print(f"👕 Virtual try-on enabled")
    print(f"📏 Fit analysis enabled")
    print(f"🔐 Authentication enabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await mongodb.close_db()
    print("👋 Shutting down gracefully")
