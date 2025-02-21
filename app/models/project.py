"""Project model."""

from app.extensions import db
from app.models.base import BaseModel


class Project(BaseModel):
    """Project model."""

    __tablename__ = "projects"

    title = db.Column(db.JSON, nullable=False)
    author = db.Column(db.JSON, nullable=False)
    date_of_completion = db.Column(db.Date, nullable=True)
    status = db.Column(
        db.Enum("ongoing", "completed", name="project_status"), nullable=False
    )
    content = db.Column(db.ARRAY(db.JSON), nullable=True)  # ARRAY of JSON objects
    tags = db.Column(db.JSON, nullable=False)
    hero_image = db.Column(db.String(255), nullable=True)
    images = db.Column(db.JSON, nullable=True)
    testimonials = db.Column(db.ARRAY(db.JSON), nullable=True)
