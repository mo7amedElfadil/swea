"""Base service class with common functionality for all services."""

from typing import Any, Dict, Optional

from marshmallow import ValidationError

from utils.db_utils import paginate_query
from utils.file_manager import FileManager


class BaseService:
    """
    A foundational service class providing core CRUD and utility operations for database models.

    The BaseService serves as an abstract base class that encapsulates common database
    interaction patterns, validation, and pagination logic. It is designed to be inherited
    by specific service classes for different domain models.

    Key Features:
    - Standardized retrieval of entities by UUID
    - Pagination support for entity listings
    - Soft and hard deletion capabilities
    - Data validation using Marshmallow schemas
    - File management integration

    Attributes:
        model_class (Type[SQLAlchemy Model]): The database model class associated with this service.
        schema (Marshmallow Schema): Schema used for data validation and serialization.
        page_size (int): Number of items to return per paginated request.
                         Defaults to 10 if not specified.
        file_manager (FileManager): Utility for handling file-related operations.

    Usage Example:
        ```
        class CourseService(BaseService):
            def __init__(self):
                super().__init__(
                    model_class=Course,
                    schema_class=CourseSchema,
                    page_size=15
                )
        ```

    Note:
        This class is intended to be subclassed and should not be used directly.
        Subclasses should specify their specific model and schema classes.
    """

    def __init__(self, model_class, schema_class, page_size: int = 10):
        """
        Initialize the base service.

        Args:
            model_class: The SQLAlchemy model class for this service
            schema_class: The Marshmallow schema class for validation
            page_size: Default page size for pagination
            file_manager: Utility for handling file-related operations
        """
        self.model_class = model_class
        self.schema = schema_class()
        self.page_size = page_size if page_size > 0 else 10
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
