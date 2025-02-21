from marshmallow import Schema, ValidationError, fields, validates


class MemberSchema(Schema):
    """
    Schema for validating member data.
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
    # Optional fields
    image = fields.Str(allow_none=True)
    university_department = fields.Str(allow_none=True)

    @validates("name")
    def validate_name(self, value: str):
        """Validate that the name is not empty."""
        if not value.strip():
            raise ValidationError("Name cannot be empty.")
