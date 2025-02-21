"""News model."""

from app.extensions import db
from app.models.base import BaseModel


class News(BaseModel):
    """News model."""

    __tablename__ = "news"

    title = db.Column(db.JSON, nullable=False)
    date = db.Column(db.Date, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.JSON, nullable=False)
    url_redirect = db.Column(db.String(255), nullable=True)
