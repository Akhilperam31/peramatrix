import sqlite3
import logging
from fastapi import APIRouter, Depends, HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from ..database import get_db_connection
from ..models import RegisterModel, LoginModel
from ..utils import send_email
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/register")
def register(data: RegisterModel, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (data.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail='Email already registered')
        
    password_hash = generate_password_hash(data.password)
    cursor.execute('INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
                   (data.name, data.email, password_hash, data.role))
    db.commit()
    
    # Send welcome email
    subject = 'Welcome to Peramatrix Learn!'
    body = f"""
    <p>Hello {data.name},</p>
    <p>You have been registered as a {data.role.title()} on Peramatrix Learn.</p>
    <p>Thank you!</p>
    """
    settings = get_settings()
    if settings.EMAIL_TO:
         send_email(data.email, subject, body)

    return {'success': True}

@router.post("/login")
def login(data: LoginModel, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute('SELECT id, name, email, password_hash, role FROM users WHERE email = ?', (data.email,))
    row = cursor.fetchone()
    
    if not row:
         raise HTTPException(status_code=401, detail='Invalid credentials')

    user = dict(row)
    
    if not check_password_hash(user['password_hash'], data.password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
        
    return {
        'success': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
    }
