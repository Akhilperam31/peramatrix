import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/hr", tags=["files"])

@router.get("/download/{filename:path}")
async def download_file(filename: str):
    if os.path.exists(filename):
        return FileResponse(filename, filename=os.path.basename(filename))
        
    potential_paths = [
        f"{filename}",           
        f"data/{filename}",      
        f"offer_letters/{filename}" 
    ]
    
    for path in potential_paths:
        if os.path.exists(path):
            return FileResponse(path, filename=os.path.basename(path))
            
    return {"error": "File not found", "searched_paths": potential_paths}
