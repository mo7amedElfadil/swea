from marshmallow import Schema, ValidationError, fields, validates


class UserSchema(Schema):
    """
    Schema for validating user data.
    """

    # Required fields
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email format.",
        },
    )
    username = fields.Str(
        required=True, error_messages={"required": "Username is required."}
    )
    password = fields.Str(
        required=True, error_messages={"required": "Password is required."}
    )

    @validates("username")
    def validate_username(self, value: str):
        """Validate that the username is not empty."""
        if not value.strip():
            raise ValidationError("Username cannot be empty.")

    @validates("password")
    def validate_password(self, value: str):
        """Validate that the password meets minimum length requirements."""
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
