"""
Course Service Module
"""

from typing import Any, Dict, List, Optional

from marshmallow import ValidationError

from app.models.course import Course, CourseMember
from app.schemas.course_schema import CourseSchema
from utils.db_utils import search_by_multilang_field
from utils.file_manager import FileManager
from utils.form_utils import parse_nested_field
from utils.service_base import BaseService


class CourseService(BaseService):
    """Course service class."""

    def __init__(self, page_size: int = 10):
        """Initialize course service."""
        super().__init__(Course, CourseSchema, page_size)

    def create_course(self, form_data: Dict[str, Any], files: Dict[str, Any]) -> Course:
        """
        Create a new course.

        Args:
            form_data: Dictionary containing course data from the form.
            files: Dictionary containing uploaded files (e.g., image).

        Returns:
            The created Course instance.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Create the course
            course = Course()
            course.create(**processed_data)
            return course

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_course(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Optional[Course]:
        """
        Update an existing course.

        Args:
            uuid: The UUID of the course to update.
            form_data: Dictionary containing updated course data.
            files: Dictionary containing updated files (e.g., image).

        Returns:
            The updated Course instance if found, otherwise None.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Retrieve the course by UUID
            course = Course.get_byuuid(uuid)
            if course:
                course.update(**processed_data)
                return course

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def add_members_to_course(self, course_uuid: str, member_uuids: List[str]) -> bool:
        """
        Add members to a course.

        Args:
            course_uuid: The UUID of the course.
            member_uuids: List of UUIDs of members to add.

        Returns:
            True if members were successfully added, False otherwise.
        """
        course = Course.get_byuuid(course_uuid)
        if not course:
            return False

        # Add members to the course
        for member_uuid in member_uuids:
            course_member = CourseMember(
                course_uuid=course_uuid, member_uuid=member_uuid
            )
            course_member.create()

        return True

    def remove_members_from_course(
        self, course_uuid: str, member_uuids: List[str]
    ) -> bool:
        """
        Remove members from a course.

        Args:
            course_uuid: The UUID of the course.
            member_uuids: List of UUIDs of members to remove.

        Returns:
            True if members were successfully removed, False otherwise.
        """
        course = Course.get_byuuid(course_uuid)
        if not course:
            return False

        # Remove members from the course
        for member_uuid in member_uuids:
            course_member = CourseMember.query.filter_by(
                course_uuid=course_uuid, member_uuid=member_uuid
            ).first()
            if course_member:
                course_member.delete(permanent=True)

        return True

    def search_courses_by_title(self, title: str) -> Dict[str, Any]:
        """
        Search for courses by title.

        Args:
            title: The search term to look for in the title field.

        Returns:
            Dictionary containing search results and pagination metadata.
        """
        return search_by_multilang_field(Course, "title", title)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process and validate form data for creating/updating a course.

        Args:
            form_data: Dictionary containing course data from the form.
            files: Dictionary containing uploaded files (e.g., image).

        Returns:
            Processed and validated data dictionary.
        """
        processed_data = {
            "title": parse_nested_field(form_data, "title"),
            "course_name": parse_nested_field(form_data, "course_name"),
            "description": parse_nested_field(form_data, "description"),
            "tags": {
                "en": self._parse_tags(form_data.get("tags[en]")),
                "ar": self._parse_tags(form_data.get("tags[ar]")),
            },
            "date": form_data.get("date"),  # Optional field
            "url": form_data.get("url"),  # Optional field
        }

        # Handle image upload
        image = files.get("image")
        if image and image.filename:
            processed_data["image"] = FileManager(image).save()

        return processed_data

    def _parse_tags(self, tags_str: Optional[str]) -> List[str]:
        """Parse tags string into a list of trimmed tags."""
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(",") if tag.strip()]
