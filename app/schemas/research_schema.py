from typing import Dict, List

from marshmallow import Schema, ValidationError, fields, validates


class ResearchSchema(Schema):
    """
    Schema for validating research data.
    """

    # Required fields
    title = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Title is required."},
    )
    author = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Author is required."},
    )
    tags = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Str()),
        required=True,
        error_messages={"required": "Tags are required."},
    )
    # Optional fields
    date_of_completion = fields.Date(allow_none=True)
    content = fields.List(fields.Dict(), allow_none=True)
    hero_image = fields.Str(allow_none=True)
    images = fields.List(fields.Str(), allow_none=True)
    testimonials = fields.List(fields.Dict(), allow_none=True)

    @validates("title")
    def validate_title(self, value: Dict[str, str]):
        """Validate that the title contains at least one language."""
        if not value:
            raise ValidationError("Title must contain at least one language.")

    @validates("author")
    def validate_author(self, value: Dict[str, str]):
        """Validate that the author contains a name and email."""
        if "name" not in value or "email" not in value:
            raise ValidationError("Author must contain 'name' and 'email'.")

    @validates("tags")
    def validate_tags(self, value: Dict[str, List[str]]):
        """Validate that tags are provided for at least one language."""
        if not value:
            raise ValidationError("Tags must be provided for at least one language.")
