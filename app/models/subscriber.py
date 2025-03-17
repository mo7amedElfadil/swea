"""Subscriber model."""

from app.extensions import db
from app.models.base import BaseModel


class Subscriber(BaseModel):
    """Subscriber model."""

    __tablename__ = "subscribers"

    email = db.Column(db.String(255), unique=True, nullable=False)
