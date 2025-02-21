"""Podcast model and association table for many-to-many relationship between Podcast and Member."""

from app.extensions import db
from app.models.base import BaseModel


class Podcast(BaseModel):
    """Podcast model."""

    __tablename__ = "podcasts"

    title = db.Column(db.JSON, nullable=False)
    podcast_name = db.Column(db.JSON, nullable=False)
    date = db.Column(db.Date, nullable=True)
    description = db.Column(db.JSON, nullable=False)
    url = db.Column(db.String(255), nullable=True)
    members = db.relationship(
        "Member", secondary="podcast_members", backref="podcasts", lazy=True
    )
    tags = db.Column(db.JSON, nullable=False)
    image = db.Column(db.String(255), nullable=True)


# Association Table for many-to-many Relationship between Podcast and Member
class PodcastMember(BaseModel):
    """Association table for Podcast and Member many-to-many Relationship."""

    __tablename__ = "podcast_members"

    podcast_uuid = db.Column(
        db.String(36),
        db.ForeignKey("podcasts.uuid", ondelete="CASCADE"),
        primary_key=True,
    )
    member_uuid = db.Column(
        db.String(36),
        db.ForeignKey("members.uuid", ondelete="CASCADE"),
        primary_key=True,
    )
