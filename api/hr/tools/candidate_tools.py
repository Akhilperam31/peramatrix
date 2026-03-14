from sqlalchemy.orm import Session
from api.hr.database import SessionLocal
from api.hr.models import Application
from crewai.tools import tool
import logging

logger = logging.getLogger(__name__)

@tool
def add_candidate_details(name: str, email: str, phone: str = "N/A", experience: str = "N/A", skills: str = "N/A") -> str:
    """Adds or updates candidate details in the database. Primary key is email."""
    db = SessionLocal()
    try:
        # Normalize inputs
        email = email.strip().lower()
        name = name.strip()
        
        # Search by email (most reliable)
        app = db.query(Application).filter(Application.email == email).first()
        
        if app:
            app.candidate_name = name
            app.phone = phone
            action = "Updated"
        else:
            # Check by name as fallback if email not found
            app_by_name = db.query(Application).filter(Application.candidate_name == name).first()
            if app_by_name:
                app_by_name.email = email
                app_by_name.phone = phone
                app = app_by_name
                action = "Updated (matched by name)"
            else:
                # If truly not found, we can't create without a job_id in this context
                return f"Candidate {name} ({email}) not found in existing applications. Evaluation halted."
            
        db.commit()
        return f"Candidate {name} {action} successfully in database."
    except Exception as e:
        db.rollback()
        logger.error(f"Error in add_candidate_details: {str(e)}")
        return f"Error updating candidate: {str(e)}"
    finally:
        db.close()

@tool
def update_candidate_status(name: str, score: float, status: str, justification: str) -> str:
    """Updates the evaluation status and score for a candidate. Handles type conversion for score."""
    db = SessionLocal()
    try:
        # Ensure score is a float and handle potential string inputs from agents
        try:
            clean_score = float(score) if score and str(score).strip() else 0.0
        except (ValueError, TypeError):
            clean_score = 0.0

        # Search by name
        app = db.query(Application).filter(Application.candidate_name == name).first()
        if not app:
            # Fallback: search for similar names if exact match fails
            app = db.query(Application).filter(Application.candidate_name.ilike(f"%{name}%")).first()

        if app:
            app.score = clean_score
            app.status = status
            app.justification = justification
            db.commit()
            return f"Status updated for {app.candidate_name} in database. Score: {clean_score}"
        else:
            return f"Candidate {name} not found in database for status update."
    except Exception as e:
        db.rollback()
        logger.error(f"Error in update_candidate_status: {str(e)}")
        return f"Error updating status: {str(e)}"
    finally:
        db.close()

@tool
def get_candidate_details(name: str) -> str:
    """Retrieves candidate details from the database using name or partial name match."""
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.candidate_name == name).first()
        if not app:
             app = db.query(Application).filter(Application.candidate_name.ilike(f"%{name}%")).first()
             
        if app:
            return f"Name: {app.candidate_name}, Email: {app.email}, Status: {app.status}, Score: {app.score}"
        else:
            return f"Candidate {name} not found in database."
    finally:
        db.close()
