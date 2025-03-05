"""Base service class with common functionality for all services."""

from math import ceil
from typing import Any, Dict, Optional

from marshmallow import ValidationError

from utils.db_utils import paginate_query


class BaseService:
    """Base service class with common functionality for all services."""

    def __init__(self, model_class, schema_class, page_size: int = 10):
        """
        Initialize the base service.

        Args:
            model_class: The SQLAlchemy model class for this service
            schema_class: The Marshmallow schema class for validation
            page_size: Default page size for pagination
        """
        self.model_class = model_class
        self.schema = schema_class()
        self.page_size = page_size

    def get_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an entity by its UUID.

        Args:
            uuid: The UUID of the entity to retrieve

        Returns:
            Dictionary representation of the entity if found, otherwise None
        """
        entity = self.model_class.get_byuuid(uuid)
        if entity:
            return entity.to_dict()
        return None

    def get_all(self, page: int = 1, **kw) -> Dict[str, Any]:
        """
        Retrieve all entities with pagination.

        Args:
            page: Page number to retrieve (default is 1)

        Returns:
            Dictionary with items and pagination metadata
        """
        pagination = self.model_class.query.filter_by(deleted_at=None, **kw)\
                .paginate(page=page, per_page=self.page_size)
        total_pages = ceil(pagination._query_count() / self.page_size)
        next_page = page + 1 if pagination.has_next else None
        data = [t.to_dict() for t in pagination.items]

        return dict(
            data=data,
            total_pages=total_pages,
            page=page,
            next_page=next_page,
        )

    def delete(self, uuid: str, permanent: bool = False) -> bool:
        """
        Delete an entity.

        Args:
            uuid: The UUID of the entity to delete
            permanent: If True, permanently delete the entity

        Returns:
            True if entity was deleted, False if not found
        """
        entity = self.model_class.get_byuuid(uuid)
        if entity:
            entity.delete(permanent=permanent)
            return True
        return False

    def restore(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Restore a soft-deleted entity.

        Args:
            uuid: The UUID of the entity to restore

        Returns:
            Dictionary representation of the restored entity if found, otherwise None
        """
        entity = self.model_class.get_byuuid(uuid)
        if entity and entity.deleted_at:
            entity.restore()
            return entity.to_dict()
        return None

    def validate_with_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data using the schema.

        Args:
            data: The data to validate

        Returns:
            The validated data

        Raises:
            ValidationError: If validation fails
        """
        errors = self.schema.validate(data)
        if errors:
            raise ValidationError(errors)
        return data
