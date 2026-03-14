from typing import Optional
from pydantic import BaseModel

class ContactModel(BaseModel):
    name: str
    email: str
    message: str
    subject: Optional[str] = ""
    company: Optional[str] = ""
    phone: Optional[str] = ""

class DemoRequestModel(BaseModel):
    name: str
    email: str
    company: Optional[str] = ""
    phone: Optional[str] = ""
    product: Optional[str] = ""
    demoDate: Optional[str] = ""
    message: Optional[str] = ""

class RegisterModel(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "student"

class LoginModel(BaseModel):
    email: str
    password: str

class ChatModel(BaseModel):
    question: str

class ToolModel(BaseModel):
    name: str
    description: str
    type: str

class CourseModel(BaseModel):
    title: str
    description: str
    category: str
    level: str
    duration: int
    instructor: str
    email: str # For role check
    
class AssessmentSubmitModel(BaseModel):
    answers: dict
