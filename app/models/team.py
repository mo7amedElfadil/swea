"""Team model."""

from app.extensions import db
from app.models.base import BaseModel


class Team(BaseModel):
    """Team model."""

    __tablename__ = "teams"

    name = db.Column(db.JSON, nullable=False)  # {"ar": "اسم الفريق", "en": "Team Name"}
    role = db.Column(db.JSON, nullable=False)
    bio = db.Column(db.JSON, nullable=False)
    socials = db.Column(db.JSON, nullable=True)
    image = db.Column(db.String(255), nullable=True)
