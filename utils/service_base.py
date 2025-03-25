"""Base service class with common functionality for all services."""

from typing import Any, Dict, Optional

from marshmallow import ValidationError

from utils.db_utils import paginate_query
from utils.file_manager import FileManager


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
        self.file_manager = FileManager

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

    def get_all(self, page: int = 1, **filters) -> Dict[str, Any]:
        """
        Retrieve all entities with search and pagination.

        Args:
            page: Page number to retrieve (default is 1)
            **filters: Additional filters to apply

        Returns:
            Dictionary with items and pagination metadata
        """
        return paginate_query(
            self.model_class, page=page, page_size=self.page_size, **filters
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
