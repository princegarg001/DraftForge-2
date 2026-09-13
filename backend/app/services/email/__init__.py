from app.services.email.base import EmailMessage, EmailProvider, SendResult
from app.services.email.outbox import dispatch
from app.services.email.providers import get_email_provider
from app.services.email.templates import (
    RenderedEmail,
    render_student_invitation,
    render_welcome,
)

__all__ = [
    "EmailMessage",
    "EmailProvider",
    "RenderedEmail",
    "SendResult",
    "dispatch",
    "get_email_provider",
    "render_student_invitation",
    "render_welcome",
]
