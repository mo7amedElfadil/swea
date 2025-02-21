from marshmallow import Schema, ValidationError, fields, validates


class ContactSchema(Schema):
    """
    Schema for validating contact data.
    """

    # Required fields
    name = fields.Str(required=True, error_messages={"required": "Name is required."})
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email format.",
        },
    )
    content = fields.Str(
        required=True, error_messages={"required": "Content is required."}
    )

    @validates("name")
    def validate_name(self, value: str):
        """Validate that the name is not empty."""
        if not value.strip():
            raise ValidationError("Name cannot be empty.")

    @validates("content")
    def validate_content(self, value: str):
        """Validate that the content is not empty."""
        if not value.strip():
            raise ValidationError("Content cannot be empty.")
