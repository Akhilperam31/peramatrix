import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import socketio

from api.config import get_settings
from api.database import init_db
from api.routers import auth, courses, tools, main

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Initialization ---
settings = get_settings()
init_db()

app = FastAPI(
    title="Peramatrix Backend",
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

# --- SocketIO ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# --- Include Routers ---
app.include_router(main.router)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(tools.router)

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
    port = int(os.environ.get("PORT", 5000))
    is_dev = settings.ENVIRONMENT == "development"
    
    if is_dev:
        logger.info("Running in DEVELOPMENT mode")
    else:
        logger.info("Running in PRODUCTION mode")
        
    uvicorn.run(
        "run:socket_app", 
        host="0.0.0.0", 
        port=port, 
        reload=is_dev,
        reload_excludes=["*.db", "*.sqlite", "*.sqlite3", "*.csv", "data/*", "hr_src/data/*"],
        log_level="info" if is_dev else "warning"
    )
