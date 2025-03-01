from typing import Any, Dict, List, Optional

from marshmallow import ValidationError

from app.models.course import Course
from app.models.member import Member
from app.schemas.course_schema import CourseSchema
from utils.db_utils import search_by_multilang_field
from utils.file_utils import handle_file_upload
from utils.form_utils import parse_nested_field, parse_tags
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
            form_data: Dictionary containing form data for the course.
            files: Dictionary containing uploaded files (e.g., image).

        Returns:
            The created Course instance.

        Raises:
            ValidationError: If form data validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Create the course
            course = Course()
            course.create(**processed_data)

            # Handle members association
            member_uuids = form_data.get("members", [])
            self._associate_members(course, member_uuids)

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
            form_data: Dictionary containing updated form data.
            files: Dictionary containing updated files (e.g., image).

        Returns:
            The updated Course instance if found, otherwise None.

        Raises:
            ValidationError: If form data validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Retrieve the course by UUID
            course = Course.get_byuuid(uuid)
            if course:
                # Update the course
                course.update(**processed_data)

                # Handle members association
                member_uuids = form_data.get("members", [])
                self._associate_members(course, member_uuids)

                return course

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def search_courses_by_title(self, title: str) -> List[Dict[str, Any]]:
        """
        Search for courses by title.

        Args:
            title: The title to search for.

        Returns:
            A list of dictionaries representing the matching courses.
        """
        return search_by_multilang_field(Course, "title", title)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process and validate form data for creating/updating a course.

        Args:
            form_data: Dictionary containing form data.
            files: Dictionary containing uploaded files.

        Returns:
            A dictionary of processed and validated data.
        """
        processed_data = {
            "title": parse_nested_field(form_data, "title"),
            "course_name": parse_nested_field(form_data, "course_name"),
            "description": parse_nested_field(form_data, "description"),
            "tags": parse_tags(form_data.get("tags")),
            "date": form_data.get("date"),
            "url": form_data.get("url"),
        }

        # Handle image upload
        image = files.get("image")
        if image and image.filename:
            processed_data["image"] = handle_file_upload(image)

        return processed_data

    def _associate_members(self, course: Course, member_uuids: List[str]):
        """
        Associate members with a course.

        Args:
            course: The Course instance to associate members with.
            member_uuids: List of member UUIDs to associate with the course.
        """
        course.members.clear()
        for member_uuid in member_uuids:
            member = Member.get_byuuid(member_uuid)
            if member:
                course.members.append(member)
