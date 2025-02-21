"""Research models."""

from app.extensions import db
from app.models.base import BaseModel


class Research(BaseModel):
    """Research model."""

    __tablename__ = "research"

    title = db.Column(db.JSON, nullable=False)
    author = db.Column(db.JSON, nullable=False)
    date_of_completion = db.Column(db.Date, nullable=True)
    content = db.Column(db.ARRAY(db.JSON), nullable=True)
    tags = db.Column(db.JSON, nullable=False)
    hero_image = db.Column(db.String(255), nullable=True)
    images = db.Column(db.JSON, nullable=True)
    testimonials = db.Column(db.ARRAY(db.JSON), nullable=True)
