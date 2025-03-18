from marshmallow import Schema, ValidationError, fields, validates


class AuthorSchema(Schema):
    """
    Schema for validating author data.
    """

    name = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Author name is required."},
    )
    email = fields.Str(allow_none=True)


class ProjectSchema(Schema):
    """
    Schema for validating project data.
    """

    # Required fields
    title = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        required=True,
        error_messages={"required": "Title is required."},
    )

    author = fields.Nested(
        AuthorSchema,  # Accepts both dict (for 'name') and str (for 'email')
        required=True,
        error_messages={"required": "Author is required."},
    )

    status = fields.Str(
        required=True,
        error_messages={"required": "Status is required."},
        validate=lambda x: x in ["ongoing", "completed"],
    )

    # Optional fields
    tags = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Str()),
        allow_none=True,
    )
    date_of_completion = fields.Date(allow_none=True)
    content = fields.List(fields.Dict(), allow_none=True)
    hero_image = fields.Str(allow_none=True)
    testimonials = fields.List(fields.Dict(), allow_none=True)

    @validates("title")
    def validate_title(self, value):
        """Ensure the title contains at least one language."""
        if not value or not any(value.values()):
            raise ValidationError("Title must contain at least one language.")

    @validates("author")
    def validate_author(self, value):
        """Ensure the author contains a name (with at least one language)."""
        if (
            "name" not in value
            or not isinstance(value["name"], dict)
            or not any(value["name"].values())
        ):
            raise ValidationError(
                "Author must contain a 'name' with at least one language."
            )
