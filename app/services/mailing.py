import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from jinja2 import Template

from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
)
logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""

    def __init__(self):
        """Initialize the EmailService with SMTP credentials."""
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_pass = Config.SMTP_PASS
        self.sender_name = "SWEA"

    def send_email(self, context: Dict[str, Any]) -> bool:
        """Send an email with the provided template and context."""
        try:
            # Prepare email message
            msg = MIMEMultipart()
            msg["Subject"] = context["subject"]
            msg["From"] = f"{self.sender_name} <{self.smtp_user}>"
            msg["To"] = context["recipient"]
            msg["List-Unsubscribe"] = (
                "<mailto:sweasd.unsubscribe@gmail.com>, <https://sweasd.org/unsubscribe>"
            )
            recipient = context["recipient"]

            # Render email content
            email_content = self.render_template(
                context["template"], context["data"]
            )
            email_content = email_content.encode("utf-8", "replace").decode(
                "utf-8"
            )
            msg.attach(MIMEText(email_content, "html", "utf-8"))

            # Connect and send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_user, recipient, msg.as_string())

            logger.info("Email sent successfully to %s", recipient)

            return True

        except Exception as e:
            logger.error(
                "Failed to send email to %s: %s", context["recipient"], str(e)
            )

            return False

    def render_template(
        self, template_name: str, context: Dict[str, Any]
    ) -> str:
        """Render an email template with the given context."""
        template = f"app/templates/{template_name}"
        with open(template, "r", encoding="utf-8") as file:
            template_str = file.read()

        jinja_template = Template(template_str)
        return jinja_template.render(context)
