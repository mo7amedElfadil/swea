from marshmallow import Schema, fields, validate


class SubscriberSchema(Schema):
    """
    Schema for validating subscriber data.
    """

    email = fields.Str(
        required=True,
        error_messages={"required": "Subscriber Email is required."},
        validate=validate.Email(),
    )
