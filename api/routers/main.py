import sqlite3
import logging
import random
from fastapi import APIRouter, Depends, HTTPException, Request
from ..database import get_db_connection
from ..models import ContactModel, DemoRequestModel, ChatModel
from ..utils import send_email
from ..config import get_settings
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["main"])

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "peramatrix-backend",
        "version": "2.0.0"
    }

@router.post("/contact")
def contact(data: ContactModel, request: Request,  db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO submissions (type, name, email, company, phone, subject, message, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('contact', data.name, data.email, data.company, data.phone, data.subject, data.message, 
              request.client.host, request.headers.get('User-Agent', '')))
        db.commit()
        
        settings = get_settings()

        # 1. Admin Notification
        subject = f'Contact Form: {data.name}'
        html_body = f"""
        <h3>New Contact Form Submission</h3>
        <p><strong>Name:</strong> {data.name}</p>
        <p><strong>Email:</strong> {data.email}</p>
        <p><strong>Company:</strong> {data.company}</p>
        <p><strong>Phone:</strong> {data.phone}</p>
        <p><strong>Subject:</strong> {data.subject}</p>
        <p><strong>Message:</strong></p>
        <p>{data.message}</p>
        """
        if settings.EMAIL_TO:
             send_email(settings.EMAIL_TO, subject, html_body)
        
        # 2. User Confirmation
        user_subject = "We received your message - Peramatrix"
        user_html_body = f"""
        <p>Hi {data.name},</p>
        <p>Thank you for contacting Peramatrix. We have received your message and will get back to you shortly.</p>
        <br>
        <p>Best regards,</p>
        <p>The Peramatrix Team</p>
        """
        if data.email:
            send_email(data.email, user_subject, user_html_body)

        return {'success': True, 'message': 'Message sent!'}
            
    except Exception as e:
        logger.error(f'Contact error: {e}')
        raise HTTPException(status_code=500, detail='Internal error')

@router.post("/demo-request")
def demo_request(data: DemoRequestModel, request: Request, db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO submissions (type, name, email, company, phone, product, demo_date, message, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('demo_request', data.name, data.email, data.company, data.phone, data.product, data.demoDate, data.message, 
              request.client.host, request.headers.get('User-Agent', '')))
        db.commit()

        settings = get_settings()
        
        # 1. Admin Notification
        subject = f'Demo Request: {data.name}'
        html_body = f"""
        <h3>New Demo Request</h3>
        <p><strong>Name:</strong> {data.name}</p>
        <p><strong>Email:</strong> {data.email}</p>
        <p><strong>Company:</strong> {data.company}</p>
        <p><strong>Phone:</strong> {data.phone}</p>
        <p><strong>Product:</strong> {data.product}</p>
        <p><strong>Preferred Date:</strong> {data.demoDate}</p>
        <p><strong>Message:</strong></p>
        <p>{data.message}</p>
        """
        if settings.EMAIL_TO:
             send_email(settings.EMAIL_TO, subject, html_body)

        # 2. User Confirmation
        user_subject = "Demo Request Received - Peramatrix"
        user_html_body = f"""
        <p>Hi {data.name},</p>
        <p>Thank you for requesting a demo. We have received your request for <strong>{data.product}</strong>.</p>
        <p>Our team will contact you shortly to schedule the demo.</p>
        <br>
        <p>Best regards,</p>
        <p>The Peramatrix Team</p>
        """
        if data.email:
            send_email(data.email, user_subject, user_html_body)
        
        return {'success': True, 'message': 'Demo request received!'}
    except Exception as e:
        logger.error(f'Demo request error: {e}')
        raise HTTPException(status_code=500, detail='Internal error')

@router.get("/dashboard")
def dashboard():
    return {
        'streak': random.randint(5, 15),
        'coursesCompleted': random.randint(8, 20),
        'totalCourses': 25,
        'timeSpent': random.randint(1200, 2000),
        'weeklyProgress': [random.randint(60, 90) for _ in range(7)]
    }

@router.post("/ai/chat")
def ai_chat(data: ChatModel):
    question = data.question.lower()
    
    response = "I'm here to help you learn! Ask me about Python, Machine Learning, or Math."
    if 'python' in question:
        response = "Python is great for data science and web dev."
    elif 'machine learning' in question:
        response = "Machine Learning allows computers to learn from data."
        
    return {'answer': response, 'timestamp': datetime.now().isoformat()}
