"""Course model and Association Table for many-to-many Relationship between Course and Member."""

from app.extensions import db
from app.models.base import BaseModel


class Course(BaseModel):
    """Course model."""

    __tablename__ = "courses"

    title = db.Column(db.JSON, nullable=False)
    course_name = db.Column(db.JSON, nullable=False)
    date = db.Column(db.Date, nullable=True)
    description = db.Column(db.JSON, nullable=False)
    url = db.Column(db.String(255), nullable=True)
    members = db.relationship(
        "Member", secondary="course_members", backref="courses", lazy=True
    )
    tags = db.Column(db.JSON, nullable=False)
    image = db.Column(db.String(255), nullable=True)


# Association Table for many-to-many Relationship between Course and Member
class CourseMember(BaseModel):
    """Association table for Course and Member many-to-many Relationship."""

    __tablename__ = "course_members"

    course_uuid = db.Column(
        db.String(36),
        db.ForeignKey("courses.uuid", ondelete="CASCADE"),
        primary_key=True,
    )
    member_uuid = db.Column(
        db.String(36),
        db.ForeignKey("members.uuid", ondelete="CASCADE"),
        primary_key=True,
    )
