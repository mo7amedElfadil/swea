import re

from marshmallow import Schema, ValidationError, fields, validates


class SubscriberSchema(Schema):
    """
    Schema for validating subscriber data.
    """

    email = fields.Str(
        required=True, error_messages={"required": "Subscriber Email is required."}
    )

    @validates("email")
    def validate_email(self, value: str):
        """Validate that the email is not empty."""
        if not value.strip():
            raise ValidationError("Email cannot be empty.")

        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not isinstance(value, str) or not re.match(email_pattern, value):
            raise ValidationError("Invalid email format in 'email' field.")
