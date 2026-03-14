import os
import shutil
import re
from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from api.hr.database import get_db
from api.hr.models import Job, Application
from api.hr.utils import get_pdf_text, get_docx_text
from api.hr.crew import RecruitmentCrew

router = APIRouter(prefix="/api/hr", tags=["hr"])

@router.get("/hr_dashboard/{user_id}")
async def hr_dashboard(user_id: int, db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    applications = db.query(Application).all()
    
    jobs_data = [{"id": j.id, "title": j.title, "description": j.description, "file_path": j.file_path} for j in jobs]
    apps_data = [
        {
            "id": a.id, 
            "job_id": a.job_id, 
            "job_title": a.job.title if a.job else "Unknown",
            "candidate_name": a.candidate_name, 
            "email": a.email, 
            "score": a.score, 
            "status": a.status, 
            "interview_status": a.interview_status, 
            "is_selected": a.is_selected,
            "resume_path": a.resume_path,
            "offer_letter_path": a.offer_letter_path
        } for a in applications
    ]
    return {"jobs": jobs_data, "applications": apps_data}

@router.post("/upload_jd/{user_id}")
async def upload_jd(user_id: int, title: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"data/{file.filename}"
    os.makedirs("data", exist_ok=True)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    # Extract text for description preview
    if file_location.endswith('.docx'):
        description = get_docx_text(file_location)
    else:
        description = "PDF/Text Content" # Simpler for now
        
    new_job = Job(title=title, description=description, file_path=file_location)
    db.add(new_job)
    db.commit()
    return {"message": "Job posted successfully"}

@router.delete("/delete_job/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    db.query(Application).filter(Application.job_id == job_id).delete()
    db.query(Job).filter(Job.id == job_id).delete()
    db.commit()
    return {"message": "Job deleted successfully"}

@router.post("/evaluate/{application_id}")
def evaluate_application(application_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    job = db.query(Job).filter(Job.id == app.job_id).first()
    
    if app.resume_path.endswith('.pdf'):
        resume_content = get_pdf_text(app.resume_path)
    else:
        resume_content = "Resume content unavailable"

    crew = RecruitmentCrew(resume_content, job.description)
    screening_crew = crew.screening_crew()
    result = screening_crew.kickoff()
    
    score = 0
    status = "Evaluated"
    result_lower = str(result).lower()
    
    if "not shortlisted" in result_lower:
        status = "Rejected"
        score = 40
        app.interview_status = "N/A"
    elif "shortlisted" in result_lower:
        status = "Shortlisted"
        score = 85
        app.interview_status = "Pending"
    else:
         status = "Rejected"
         score = 40
         app.interview_status = "N/A"

    app.score = score
    app.status = status
    app.justification = str(result)
    db.commit()
    
    return {"message": "Evaluation completed", "score": score, "status": status}

@router.post("/select_candidate/{application_id}")
def select_candidate(application_id: int, decision: str = Form(...), ctc: str = Form(None), db: Session = Depends(get_db)):
    job_app = db.query(Application).filter(Application.id == application_id).first()
    job = db.query(Job).filter(Job.id == job_app.job_id).first()
    
    if job_app.resume_path.endswith('.pdf'):
        resume_content = get_pdf_text(job_app.resume_path)
    elif job_app.resume_path.endswith('.docx'):
        resume_content = get_docx_text(job_app.resume_path)
    else:
        resume_content = "Content unavailable"

    crew = RecruitmentCrew(resume_content, job.description)
    crew.offer.description += f"\n\nRESUME CONTENT:\n{resume_content}"
    offer_crew = crew.offer_crew()
    
    inputs = {'decision': decision, 'ctc': ctc if ctc else "N/A"}
    result = offer_crew.kickoff(inputs=inputs)
    result_str = str(result)
    
    if decision == "Selected":
        filename = None
        match = re.search(r'(Offer_Letter_.*?\.pdf)', result_str)
        if match:
            extracted = os.path.basename(match.group(1))
            if os.path.exists(f"offer_letters/{extracted}"):
                filename = extracted

        if not filename:
            name_match = re.search(r'Name:\s*(.*)', resume_content)
            if name_match:
                resume_name = name_match.group(1).strip()
                safe_resume_name = resume_name.replace(' ', '_')
                possible_file = f"Offer_Letter_{safe_resume_name}.pdf"
                if os.path.exists(f"offer_letters/{possible_file}"):
                     filename = possible_file
        
        if not filename:
            safe_name_app = str(job_app.candidate_name).replace(' ', '_')
            possible_file = f"Offer_Letter_{safe_name_app}.pdf"
            if os.path.exists("offer_letters"):
                for existing_file in os.listdir("offer_letters"):
                    if existing_file.lower() == possible_file.lower():
                        filename = existing_file
                        break
            
            if not filename:
                 try:
                    list_of_files = [os.path.join("offer_letters", f) for f in os.listdir("offer_letters") if f.lower().endswith('.pdf')]
                    if list_of_files:
                        latest_file = max(list_of_files, key=os.path.getctime)
                        filename = os.path.basename(latest_file)
                    else:
                        filename = possible_file
                 except Exception:
                    filename = possible_file

        job_app.offer_letter_path = filename
        job_app.interview_status = "Selected"
        job_app.is_selected = 1
    else:
        job_app.interview_status = "Rejected"
        job_app.is_selected = 0
        
    db.commit()
    return {"message": "Candidate selection processed"}

@router.delete("/delete_application/{application_id}")
async def delete_application(application_id: int, db: Session = Depends(get_db)):
    job_app = db.query(Application).filter(Application.id == application_id).first()
    if job_app:
        db.delete(job_app)
        db.commit()
    return {"message": "Application deleted successfully"}
