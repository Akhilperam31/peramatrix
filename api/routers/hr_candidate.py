import os
import shutil
from fastapi import APIRouter, Depends, Form, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.hr.database import get_db
from api.hr.models import User, Job, Application

router = APIRouter(prefix="/api/hr", tags=["candidate"])

@router.get("/candidate_dashboard/{user_id}")
async def candidate_dashboard(user_id: int, db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    user = db.query(User).filter(User.id == user_id).first()
    my_apps = db.query(Application).filter(Application.user_id == user_id).all()
    
    jobs_data = [{"id": j.id, "title": j.title, "description": j.description, "file_path": j.file_path} for j in jobs]
    apps_data = [
        {
            "id": a.id, 
            "job_id": a.job_id, 
            "job_title": a.job.title if a.job else "Unknown",
            "score": a.score, 
            "status": a.status, 
            "interview_status": a.interview_status,
            "offer_letter_path": a.offer_letter_path
        } for a in my_apps
    ]
    
    return {
        "user": {"id": user.id, "username": user.username} if user else None,
        "jobs": jobs_data, 
        "applications": apps_data
    }

@router.get("/jobs/{job_id}")
async def view_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    return {"id": job.id, "title": job.title, "description": job.description}

@router.post("/apply/{job_id}")
async def apply_job(
    job_id: int, 
    user_id: int = Form(...), 
    full_name: str = Form(...), 
    email: str = Form(...),
    resume: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    existing_app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user_id).first()
    if existing_app:
        return JSONResponse(status_code=400, content={"error": "You have already applied for this job."})

    file_location = f"data/{resume.filename}"
    os.makedirs("data", exist_ok=True)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(resume.file, file_object)
        
    new_app = Application(
        job_id=job_id,
        candidate_name=full_name,
        user_id=user.id,
        email=email,
        phone="1234567890",
        resume_path=file_location,
        status="Applied"
    )
    db.add(new_app)
    db.commit()
    return {"message": "Application submitted successfully"}
