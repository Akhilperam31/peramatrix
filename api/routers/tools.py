import sqlite3
import logging
from fastapi import APIRouter, Depends
from ..database import get_db_connection
from ..models import ToolModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["tools"])

@router.get("/tools")
def get_tools(db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tools ORDER BY created_at DESC")
    return [dict(row) for row in cursor.fetchall()]

@router.post("/tools")
def create_tool(data: ToolModel, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute('INSERT INTO tools (name, description, tool_type) VALUES (?, ?, ?)',
                   (data.name, data.description, data.type))
    db.commit()
    tool_id = cursor.lastrowid
    return {'id': tool_id, 'message': 'Tool created successfully'}

@router.delete("/tools/{tool_id}")
def delete_tool(tool_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute('DELETE FROM tools WHERE id = ?', (tool_id,))
    db.commit()
    return {'message': 'Tool deleted successfully'}
