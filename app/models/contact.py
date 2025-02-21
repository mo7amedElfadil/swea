"""Contact model."""

from app.extensions import db
from app.models.base import BaseModel


class Contact(BaseModel):
    """Contact model."""

    __tablename__ = "contacts"

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
