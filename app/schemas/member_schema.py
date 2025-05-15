from typing import Dict

from marshmallow import Schema, ValidationError, fields, validates


class MemberSchema(Schema):
    """
    Schema for validating member data.
    """

    # Required fields
    name = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Member name is required."},
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email format.",
        },
    )
    # Optional fields
    image = fields.Str(allow_none=True)
    university_department = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        allow_none=True,
    )

    @validates("name")
    def validate_name(self, value: Dict[str, str], **kwargs):
        """Validate that the name contains at least one language."""
        if not value:
            raise ValidationError("Name must contain at least one language.")
