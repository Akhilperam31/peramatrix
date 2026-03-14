import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from .config import get_settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, html_content: str, attachments: list = None) -> bool:
    """Send email with HTML content and optional attachments"""
    settings = get_settings()
    try:
        smtp_server = settings.SMTP_SERVER
        smtp_port = settings.SMTP_PORT
        smtp_username = settings.SMTP_USER
        smtp_password = settings.SMTP_PASSWORD
        
        if not all([smtp_username, smtp_password]):
            logger.warning("Email credentials not configured. Skipping email send.")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = to_email
        
        # Create text version by stripping some HTML or just using simple formatting
        text_content = html_content.replace('<p>', '').replace('</p>', '\n').replace('<br/>', '\n')
        
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        if attachments:
            for file_path in attachments:
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(file_path)}'
                    )
                    msg.attach(part)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def serialize_course(course):
    return {
        'id': course['id'],
        'title': course['title'],
        'description': course['description'],
        'category': course['category'],
        'level': course['level'],
        'duration': course['duration'],
        'instructor': course['instructor'],
        'rating': course['rating'],
        'students': course['students_count'],
        'isRecommended': bool(course['is_recommended']),
        'isPopular': bool(course['is_popular'])
    }
