"""Member model."""

from app.extensions import db
from app.models.base import BaseModel


class Member(BaseModel):
    """Member model."""

    __tablename__ = "members"

    name = db.Column(db.JSON, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    university_department = db.Column(db.JSON, nullable=True)
