from typing import Dict

from marshmallow import Schema, ValidationError, fields, validates


class NewsSchema(Schema):
    """
    Schema for validating news data.
    """

    # Required fields
    title = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Title is required."},
    )
    description = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Description is required."},
    )
    # Optional fields
    date = fields.Date(allow_none=True)
    image = fields.Str(allow_none=True)
    url_redirect = fields.Str(allow_none=True)

    @validates("title")
    def validate_title(self, value: Dict[str, str]):
        """Validate that the title contains at least one language."""
        if not value:
            raise ValidationError("Title must contain at least one language.")

    @validates("description")
    def validate_description(self, value: Dict[str, str]):
        """Validate that the description contains at least one language."""
        if not value:
            raise ValidationError("Description must contain at least one language.")
