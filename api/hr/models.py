from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # 'hr' or 'candidate'

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    file_path = Column(String)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    candidate_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    email = Column(String)
    phone = Column(String)
    resume_path = Column(String)
    
    # Evaluation Results
    score = Column(Float, default=0.0)
    status = Column(String, default="Applied") # Applied, Shortlisted, Rejected, Selected, Offer Sent
    justification = Column(Text)
    
    # Check if selected
    is_selected = Column(Integer, default=0) # 0: Pending/No, 1: Yes
    offer_letter_path = Column(String, nullable=True)
    interview_status = Column(String, default="Pending") # Pending, Scheduled, Selected, Rejected
    
    job = relationship("Job")
