"""User model."""

from app.extensions import db
from app.models.base import BaseModel


class User(BaseModel):
    """User model."""

    __tablename__ = "users"

    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
