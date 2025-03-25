"""
Member Service Module
"""

from typing import Any, Dict, Optional

from marshmallow import ValidationError

from app.models import Member
from app.schemas import MemberSchema
from utils.db_utils import search_by_multilang_field
from utils.form_utils import parse_nested_field
from utils.service_base import BaseService


class MemberService(BaseService):
    """Member service class."""

    def __init__(self, page_size: int = 10):
        """Initialize member service."""
        super().__init__(Member, MemberSchema, page_size)

    def create_member(self, form_data: Dict[str, Any], files: Dict[str, Any]) -> Member:
        """
        Create a new member.

        Args:
            form_data: Dictionary containing member data from the form.
            files: Dictionary containing uploaded files (e.g., image).

        Returns:
            The created Member instance.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Create the member
            member = self.model_class()
            member.create(**processed_data)
            return member

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_member(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Optional[Member]:
        """
        Update an existing member.

        Args:
            uuid: The UUID of the member to update.
            form_data: Dictionary containing updated member data.
            files: Dictionary containing updated files (e.g., image).

        Returns:
            The updated Member instance if found, otherwise None.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Retrieve the member by UUID
            member = self.model_class.get_byuuid(uuid)
            if member:
                member.update(**processed_data)
                return member

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def search_members_by_name(self, name: str) -> Dict[str, Any]:
        """
        Search for members by name.

        Args:
            name: The search term to look for in the name field.

        Returns:
            Dictionary containing search results and pagination metadata.
        """
        return search_by_multilang_field(self.model_class, "name", name)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process and validate form data for creating/updating a member.

        Args:
            form_data: Dictionary containing member data from the form.
            files: Dictionary containing uploaded files (e.g., image).

        Returns:
            Processed and validated data dictionary.
        """
        processed_data = {
            "name": parse_nested_field(form_data, "name"),
            "email": form_data.get("email"),
            "university_department": parse_nested_field(
                form_data, "university_department"
            ),
        }

        # Handle image upload
        image = files.get("image")
        if image and image.filename:
            processed_data["image"] = self.file_manager(image).save()

        return processed_data
