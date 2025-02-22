"""Base model for all DB models."""

from datetime import datetime, timezone
from uuid import uuid4

from app.extensions import db


class BaseModel(db.Model):
    """Base model for all models."""

    __abstract__ = True  # abstract class (not a table)

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    deleted_at = db.Column(db.DateTime)

    def create(self, **kwargs) -> None:
        """Create a record in the database."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs) -> None:
        """Update a record in the database."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self, permanent=False) -> None:
        """Delete a record from the database."""
        if permanent:
            db.session.delete(self)
        else:
            self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    @classmethod
    def get_all(cls) -> list:
        """Get all records from the database."""
        return cls.query.filter_by(deleted_at=None).all()

    @classmethod
    def get_byuuid(cls, uuid):
        """Get a record from the database by its ID."""
        return cls.query.filter_by(uuid=uuid, deleted_at=None).first()

    @classmethod
    def get_by(cls, **kwargs):
        """Get a record from the database by a given attribute."""
        return cls.query.filter_by(**kwargs, deleted_at=None).first()

    @classmethod
    def get_all_by(cls, **kwargs):
        """Get all records from the database by a given attribute."""
        return cls.query.filter_by(**kwargs, deleted_at=None).all()

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        """Return a string representation of the model."""
        return f"<{self.__class__.__name__} {self.uuid}>"
