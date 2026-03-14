from crewai.tools import tool
from api.utils import send_email

@tool("SendEmailTool")
def send_email_tool(recipient_email: str, subject: str, body: str, attachment_path: str = ""):
    """Sends an email using the centralized platform utility. Supports optional attachments (leave attachment_path empty if none)."""
    # CrewAI sometimes fails if optional fields are missing from dict; default to empty string
    attachments = [attachment_path] if attachment_path and len(attachment_path) > 1 else None
    
    # The centralized utility already handles HTML conversion if needed, 
    # but since agents send text, we'll wrap it in a simple <p> for better rendering
    html_body = f"<p style='white-space: pre-wrap;'>{body}</p>"
    
    success = send_email(
        to_email=str(recipient_email),
        subject=subject,
        html_content=html_body,
        attachments=attachments
    )
    
    if success:
        return f"Email sent successfully to {recipient_email}."
    else:
        return f"Failed to send email to {recipient_email}. Check server logs for details."
