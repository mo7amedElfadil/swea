"""
Subscriber service module.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from marshmallow import ValidationError

from app.models.subscriber import Subscriber
from app.queue import QueueService
from app.schemas.subscriber_schema import SubscriberSchema
from config import Config
from utils.db_utils import paginate_query
from utils.service_base import BaseService


class EmailTemplate(Enum):
    """Email template types"""

    CONFIRMATION = "email_confirmation_email_form.html"
    PASSWORD_RESET = "password_reset_email_form.html"
    CONTACT_US = "contact_us_email-form.html"
    ANNOUNCEMENT = "announcement_email_form.html"


@dataclass
class EmailConfig:
    """Email configuration data structure"""

    service: str
    recipient: str
    subject: str
    template: str
    data: Dict[str, str]


class SubscriberService(BaseService):
    """Subscriber service class."""

    def __init__(self, page_size: int = 10):
        """Initialize subscriber service."""
        super().__init__(Subscriber, SubscriberSchema, page_size)
        self.queue_service = QueueService()
        self.sender_email = Config.SMTP_USER

    def create_subscriber(self, form_data: Dict[str, Any]) -> Subscriber:
        """
        Create a new subscriber.

        Args:
            form_data: Dictionary containing subscriber data from the form.

        Returns:
            The created Subscriber instance.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Create the subscriber
            subscriber = Subscriber()
            subscriber.create(**processed_data)
            return subscriber

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def search_subscribers_by_email(self, email: str) -> Dict[str, Any]:
        """
        Search for a subscriber by email.

        Args:
            email: The email address to search for.

        Returns:
            The Subscriber instance if found, None otherwise.
        """
        return paginate_query(Subscriber, email=email)

    def delete_subscriber(self, subscriber_email: str) -> bool:
        """
        Delete a subscriber.

        Args:
            subscriber_email: The email of the subscriber to delete.

        Returns:
            True if subscriber was deleted, False if not found.
        """
        try:
            subscriber = self.search_subscribers_by_email(subscriber_email)

            if subscriber["total_items"] > 0:
                uuid = subscriber["data"][0]["uuid"]
                self.delete(uuid, permanent=True)
                return True

            return False

        except Exception as e:
            raise Exception(f"Failed to delete subscriber: {e}") from e

    def send_broadcast_email(self, form_data: Dict[str, Any]) -> None:
        """
        Send a broadcast email to all subscribers.
        Includes input validation and error handling.
        """
        try:
            email_data = self.validate_form_data(form_data, validate="broadcast")

            # Get all subscribers
            subscribers = self.get_all()
            list_of_subscribers = [
                subscriber["email"] for subscriber in subscribers["data"]
            ]

            if subscribers["total_items"] == 0:
                raise ValueError("No subscribers found")

            for subscriber in list_of_subscribers:
                email_config = EmailConfig(
                    service="SWEA",
                    recipient=subscriber,
                    subject=email_data["subject"],
                    template=EmailTemplate.ANNOUNCEMENT.value,
                    data={
                        "subject": email_data["subject"],
                        "recipient": subscriber.split("@")[0],
                        "message": email_data["message"],
                        "unsubscribe_link": f"{Config.BASE_URL}/unsubscribe?email={subscriber}",
                    },
                )

                self.queue_service.enqueue_task("send_email", email_config.__dict__)

        except ValueError as ve:
            raise ValueError(f"Invalid broadcast email: {ve}") from ve
        except Exception as e:
            raise Exception(f"Failed to send broadcast email: {e}") from e

    def validate_form_data(
        self, form_data: Dict[str, Any], validate: str = "email"
    ) -> Dict[str, Any]:
        """
        Validate the form data submitted by the user.
        Raises ValueError if validation fails.
        """
        if validate == "email":
            required_keys = {"email"}
            missing_keys = required_keys - form_data.keys()

            if missing_keys:
                raise ValueError(f"Missing required fields: {', '.join(missing_keys)}")

            return form_data

        required_keys = {"subject", "message"}
        missing_keys = required_keys - form_data.keys()

        if missing_keys:
            raise ValueError(f"Missing required fields: {', '.join(missing_keys)}")

        return form_data
