import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from api.config import get_settings
from api.routers import hr_api, hr_auth, hr_candidate, hr_files
from api.hr.database import engine as hr_engine, Base as hr_Base

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Initialization ---
settings = get_settings()
# Initialize only the HR Recruitment Database
hr_Base.metadata.create_all(bind=hr_engine)

app = FastAPI(
    title="Peramatrix HR Backend",
    version="2.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None
)

# --- Middleware ---
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- Include HR Routers ---
app.include_router(hr_api.router)
app.include_router(hr_auth.router)
app.include_router(hr_candidate.router)
app.include_router(hr_files.router)

@app.get("/api/hr/health")
async def health_check():
    return {"status": "healthy", "service": "hr_recruitment"}

# --- Static Files & SPA Routing ---
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # Skip /api routes
    if full_path.startswith("api/"):
        return {"detail": "Not Found"}
        
    file_path = os.path.join(settings.BASE_DIR, 'frontend', 'build', full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(settings.BASE_DIR, 'frontend', 'build', 'index.html'))

if __name__ == "__main__":
    port = 8000
    is_dev = settings.ENVIRONMENT == "development"
    
    logger.info(f"Starting HR Backend in {settings.ENVIRONMENT} mode on port {port}")
        
    uvicorn.run(
        "run_hr:app", 
        host="0.0.0.0", 
        port=port, 
        reload=is_dev,
        reload_excludes=["*.db", "*.sqlite", "*.sqlite3", "*.csv", "data/*"],
        log_level="info" if is_dev else "warning"
    )
