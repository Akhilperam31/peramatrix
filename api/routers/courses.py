import sqlite3
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db_connection
from ..models import CourseModel, AssessmentSubmitModel
from ..utils import serialize_course
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["courses"])

@router.get("/courses")
def get_courses(category: Optional[str] = None, level: Optional[str] = None, search: Optional[str] = None, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    
    query = "SELECT * FROM courses WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if level:
        query += " AND level = ?"
        params.append(level)
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
        
    cursor.execute(query, params)
    courses = [serialize_course(row) for row in cursor.fetchall()]
    return courses

@router.get("/courses/{course_id}")
def get_course(course_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    if not course:
        raise HTTPException(status_code=404, detail='Course not found')
    return serialize_course(course)

@router.post("/courses")
def add_course(data: CourseModel, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    
    # Check role
    cursor.execute('SELECT role FROM users WHERE email = ?', (data.email,))
    user = cursor.fetchone()
    if not user or user['role'] != 'faculty':
        raise HTTPException(status_code=403, detail='Unauthorized')

    cursor.execute('''
        INSERT INTO courses (title, description, category, level, duration, instructor)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.title, data.description, data.category, data.level, data.duration, data.instructor))
    db.commit()
    return {'success': True, 'id': cursor.lastrowid}

@router.get("/assessment/{assessment_id}/questions")
def get_assessment_questions(assessment_id: int):
    # Mock questions
    questions = {
            1: [  # Machine Learning Basics Quiz
                {
                    'id': 1,
                    'question': 'What is supervised learning?',
                    'options': [
                        'Learning without labeled data',
                        'Learning with labeled data',
                        'Learning through trial and error',
                        'Learning from environment feedback'
                    ],
                    'correct': 1
                },
                {
                    'id': 2,
                    'question': 'Which algorithm is commonly used for classification?',
                    'options': [
                        'Linear Regression',
                        'Logistic Regression',
                        'K-means Clustering',
                        'Principal Component Analysis'
                    ],
                    'correct': 1
                }
            ],
            2: [  # Data Science Assessment
                {
                    'id': 1,
                    'question': 'What is the purpose of data preprocessing?',
                    'options': [
                        'To make data look better',
                        'To clean and prepare data for analysis',
                        'To reduce data size',
                        'To encrypt data'
                    ],
                    'correct': 1
                }
            ]
        }
    if assessment_id not in questions:
         raise HTTPException(status_code=404, detail='Assessment not found')
    return questions[assessment_id]

@router.post("/assessment/{assessment_id}/submit")
def submit_assessment(assessment_id: int, data: AssessmentSubmitModel):
    answers = data.answers
    total_questions = len(answers)
    # Mock scoring: assume 1 is always the correct answer index/value for simplicity or based on legacy mock
    correct_answers = sum(1 for answer in answers.values() if answer == 1) 
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    return {
        'score': round(score, 2),
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'completed_at': datetime.now().isoformat()
    }

@router.get("/assessments")
def get_assessments(db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM assessments ORDER BY created_at DESC")
    return [dict(row) for row in cursor.fetchall()]
