from typing import Dict

from marshmallow import Schema, ValidationError, fields, validates


class TeamSchema(Schema):
    """
    Schema for validating team data.
    """

    # Required fields
    name = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Name is required."},
    )
    role = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Role is required."},
    )
    bio = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Bio is required."},
    )
    # Optional fields
    socials = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True)
    image = fields.Str(allow_none=True)

    @validates("name")
    def validate_name(self, value: Dict[str, str]):
        """Validate that the name contains at least one language."""
        if not value:
            raise ValidationError("Name must contain at least one language.")

    @validates("role")
    def validate_role(self, value: Dict[str, str]):
        """Validate that the role contains at least one language."""
        if not value:
            raise ValidationError("Role must contain at least one language.")

    @validates("bio")
    def validate_bio(self, value: Dict[str, str]):
        """Validate that the bio contains at least one language."""
        if not value:
            raise ValidationError("Bio must contain at least one language.")
