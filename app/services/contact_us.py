from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from app.services.queue_service import QueueService
from config import Config


class EmailTemplate(Enum):
    """Email template types"""

    CONFIRMATION = "email_confirmation_email_form.html"
    PASSWORD_RESET = "password_reset_email_form.html"
    CONTACT_US = "contact_us_email-form.html"


@dataclass
class EmailConfig:
    """Email configuration data structure"""

    service: str
    recipient: str
    subject: str
    template: str
    data: Dict[str, str]


class ManageContactUs:

    def __init__(self):
        """Initialize the ManageSubscription service"""
        self.queue_service = QueueService()
        self.recipient = Config.SMTP_USER

    def contact_us_message(self, form_data: Dict[str, Any]) -> None:
        """Send a message to the contact us email"""
        email_config = EmailConfig(
            service="SWEA",
            recipient=self.recipient,
            subject="Notification of new contact us message",
            template=EmailTemplate.CONTACT_US.value,
            data={
                "subject": "Notification of new contact us message",
                "recipient": self.recipient,
                "visitor_email": form_data["email"],
                "message": form_data["msg"],
                "name": form_data["name"],
            },
        )

        self.queue_service.enqueue_task("send_email", email_config.__dict__)
