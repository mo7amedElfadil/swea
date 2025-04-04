"""Team model."""

from app.extensions import db
from app.models.base import BaseModel


class Team(BaseModel):
    """Team model."""

    __tablename__ = "teams"

    name = db.Column(db.JSON, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=1)
    role = db.Column(db.JSON, nullable=False)
    bio = db.Column(db.JSON, nullable=False)
    socials = db.Column(db.JSON, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
