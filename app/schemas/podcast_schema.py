from typing import Dict, List

from marshmallow import Schema, ValidationError, fields, validates


class PodcastSchema(Schema):
    """
    Schema for validating podcast data.
    """

    # Required fields
    title = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Title is required."},
    )
    podcast_name = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Podcast name is required."},
    )
    description = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Description is required."},
    )
    tags = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Str()),
        required=True,
        error_messages={"required": "Tags are required."},
    )
    # Optional fields
    date = fields.Date(allow_none=True)
    url = fields.Str(allow_none=True)
    image = fields.Str(allow_none=True)

    @validates("title")
    def validate_title(self, value: Dict[str, str]):
        """Validate that the title contains at least one language."""
        if not value:
            raise ValidationError("Title must contain at least one language.")

    @validates("podcast_name")
    def validate_podcast_name(self, value: Dict[str, str]):
        """Validate that the podcast name contains at least one language."""
        if not value:
            raise ValidationError(
                "Podcast name must contain at least one language."
            )

    @validates("description")
    def validate_description(self, value: Dict[str, str]):
        """Validate that the description contains at least one language."""
        if not value:
            raise ValidationError(
                "Description must contain at least one language."
            )

    @validates("tags")
    def validate_tags(self, value: Dict[str, List[str]]):
        """Validate that tags are provided for at least one language."""
        if not value:
            raise ValidationError(
                "Tags must be provided for at least one language."
            )
