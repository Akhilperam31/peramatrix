from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.hr.database import get_db
from api.hr.models import User

router = APIRouter(prefix="/api/hr", tags=["auth"])

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    # Hardcoded credentials check (matching legacy app.py behavior)
    if role == "hr" and (username != "admin" or password != "admin"):
        return JSONResponse(status_code=401, content={"error": "Invalid HR credentials. Use admin/admin."})
    elif role == "candidate" and (username != "user" or password != "user"):
        return JSONResponse(status_code=401, content={"error": "Invalid Candidate credentials. Use user/user."})
        
    # Ensure user exists in database for relational mapping
    user = db.query(User).filter(User.username == username, User.role == role).first()
    if not user:
        user = User(username=username, password_hash=password, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return {"message": "Login successful", "user": {"id": user.id, "username": user.username, "role": user.role}}
