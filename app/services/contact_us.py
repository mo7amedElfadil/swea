import html
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from app.queue import QueueService
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
        """Initialize the ManageContactUs service"""
        self.queue_service = QueueService()
        self.recipient = Config.SMTP_USER

    def contact_us_message(self, form_data: Dict[str, Any]) -> None:
        """
        Send a message to the contact us email.
        Includes input validation and error handling.
        """
        try:
            self.validate_form_data(form_data)

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

        except ValueError as ve:
            raise ValueError(f"Invalid contact us message: {ve}") from ve
        except Exception as e:
            raise Exception(f"Failed to send contact us message: {e}") from e

    def validate_form_data(self, form_data: Dict[str, Any]) -> None:
        """
        Validate the form data submitted by the user.
        Raises ValueError if validation fails.
        """
        required_keys = {"name", "email", "msg"}
        missing_keys = required_keys - form_data.keys()

        if missing_keys:
            raise ValueError(f"Missing required fields: {', '.join(missing_keys)}")

        # Validate name, email, and message fields
        if not isinstance(form_data["name"], str) or not form_data["name"].strip():
            raise ValueError("Invalid or empty 'name' field.")
        form_data["name"] = self.sanitize_content(form_data["name"])
        if len(form_data["name"]) < 2 or len(form_data["name"]) > 100:
            raise ValueError("Name must be between 2 and 100 characters")

        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not isinstance(form_data["email"], str) or not re.match(
            email_pattern, form_data["email"]
        ):
            raise ValueError("Invalid email format in 'email' field.")

        if not isinstance(form_data["msg"], str) or not form_data["msg"].strip():
            raise ValueError("Invalid or empty 'msg' field.")
        form_data["msg"] = self.sanitize_content(form_data["msg"])
        if len(form_data["msg"]) < 10:
            raise ValueError("Message must be at least 10 characters long")

    def sanitize_content(self, content):
        """Sanitize user input to prevent injection attacks"""
        # Strip potentially dangerous HTML
        sanitized = html.escape(content)

        if len(sanitized) > 5000:
            sanitized = sanitized[:5000]

        return sanitized
