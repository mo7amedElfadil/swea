"""
Project Service Module

This module provides the business logic for project-related operations.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from marshmallow import ValidationError

from app.models import Project
from app.schemas import ProjectSchema
from utils.db_utils import search_by_multilang_field
from utils.service_base import BaseService


class ProjectService(BaseService):
    """Project service class."""

    def __init__(self, page_size: int = 3):
        """Initialize project service."""
        super().__init__(Project, ProjectSchema, page_size)

    def create_project(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> bool:
        """
        Create a new project.
        Args:
            form_data (Dict[str, Any]): The project data to create.
            files (Dict[str, Any]): The uploaded files.
        Returns:
            bool: True if the project was created successfully, otherwise raises
            a ValidationError.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)
            # Validate the data using the schema
            self.validate_with_schema(processed_data)

            instance = self.model_class()
            instance.create(**processed_data)
            return True  # Return True if successful
        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_project(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> bool:
        """
        Update an existing project.

        Args:
            uuid (str): The UUID of the project to update.
            form_data (Dict[str, Any]): The project data to update.
            files (Dict[str, Any]): The uploaded files.

        Returns:
            bool: True if the project was updated successfully, otherwise raises
            a ValidationError.
        """
        try:
            # Process and validate form data
            form_data = self.validate_form_data(form_data, files)

            # Validate project data
            self.validate_with_schema(form_data)

            project = self.model_class.get_byuuid(uuid)
            if project:
                project.update(**form_data)
            return True
        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def delete_project(self, uuid: str, permanent: bool = False) -> bool:
        """
        Delete a project.

        Args:
            uuid (str): The UUID of the project to delete.
            permanent (bool): If True, permanently delete the project. Otherwise, soft delete.

        Returns:
            bool: True if the project was deleted, False if the project was not found.
        """
        project = self.model_class.get_byuuid(uuid)
        if project:
            project.delete(permanent=permanent)
            return True
        return False

    def get_project_by_uuid(self, uuid: str) -> Optional[Project]:
        """
        Retrieve a project by its UUID.

        Args:
            uuid (str): The UUID of the project to retrieve.

        Returns:
            Optional[Project]: The project instance if found, otherwise None.
        """
        project = self.model_class.get_byuuid(uuid)

        # Prepare the project data for rendering
        if project:
            project_data = project.__dict__
            project_data["tags"]["en"] = ", ".join(project_data["tags"]["en"])
            project_data["tags"]["ar"] = ", ".join(project_data["tags"]["ar"])

            if isinstance(project_data["testimonials"], dict):
                project_data["testimonials"]["en"] = ", ".join(
                    project_data["testimonials"].get("en", [])
                )
                project_data["testimonials"]["ar"] = ", ".join(
                    project_data["testimonials"].get("ar", [])
                )

            return project_data

        return None

    def get_projects_by_author(self, author: Dict[str, Any]) -> List[Project]:
        """
        Retrieve all projects by a specific author.

        Args:
            author (Dict[str, Any]): The author details to filter by.

        Returns:
            List[Project]: A list of projects authored by the specified author.
        """
        return self.model_class.get_all_by(author=author)

    def get_projects_by_completion_date(
        self, date_of_completion: date
    ) -> List[Project]:
        """
        Retrieve all projects with a specific completion date.

        Args:
            date_of_completion (date): The completion date to filter by.

        Returns:
            List[Project]: A list of projects with the specified completion date.
        """
        return self.model_class.get_all_by(
            date_of_completion=date_of_completion
        )

    def search_projects_by_title(self, title: str) -> Dict[str, Any]:
        """
        Search for projects by title.

        Args:
            title (str): The title to search for.

        Returns:
            Dict[str, Any]: Dictionary containing search results and pagination
            metadata.
        """
        return search_by_multilang_field(self.model_class, "title", title)

    def restore_project(self, uuid: str) -> Optional[Project]:
        """
        Restore a soft-deleted project.

        Args:
            uuid (str): The UUID of the project to restore.

        Returns:
            Optional[Project]: The restored project instance if found, otherwise None.
        """
        project = self.model_class.get_byuuid(uuid)
        if project and project.deleted_at:
            project.restore()
            return project
        return None

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and validate form data for creating/updating a project."""
        processed_data = {
            "title": self._parse_nested_field(form_data, "title"),
            "author": {
                "name": self._parse_nested_field(form_data, "author[name]"),
                "email": self._parse_field(form_data, "author[email]"),
            },
            "status": form_data.get("status", "ongoing").strip(),
            "date_of_completion": self._parse_field(
                form_data, "date_of_completion"
            ),
            "tags": {
                "en": self._parse_tags(form_data.get("tags[en]")),
                "ar": self._parse_tags(form_data.get("tags[ar]")),
            },
            "content": self._parse_indexed_fields(form_data, files, "content"),
        }

        # Handle hero_image upload
        image = files.get("hero_image")
        if image and image.filename:
            processed_data["hero_image"] = self.handle_file_upload(image)

        # Process testimonials field
        processed_data["testimonials"] = self._parse_indexed_fields(
            form_data,
            files,
            "testimonial",
            additional_fields={
                "author": "author",
                "qualification": "qualification",
            },
        )
        return processed_data

    def _parse_nested_field(
        self, form_data: Dict[str, Any], field_prefix: str
    ) -> Dict[str, str]:
        """Parse nested fields like title[en], title[ar]."""
        return {
            "en": (
                form_data.get(f"{field_prefix}[en]").strip()
                if form_data.get(f"{field_prefix}[en]")
                else ""
            ),
            "ar": (
                form_data.get(f"{field_prefix}[ar]").strip()
                if form_data.get(f"{field_prefix}[ar]")
                else ""
            ),
        }

    def _parse_tags(self, tags_str: Optional[str]) -> List[str]:
        """Parse tags string into a list of trimmed tags."""
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

    def _parse_indexed_fields(
        self,
        form_data: Dict[str, Any],
        files: Dict[str, Any],
        field_prefix: str,
        additional_fields: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Parse indexed fields like content[0][en], content[0][ar], or testimonials[0][en], testimonials[0][author].

        Args:
            form_data: The form data dictionary.
            files: The files dictionary.
            field_prefix: The prefix for the indexed fields (e.g., "content" or "testimonial").
            additional_fields: A dictionary of additional fields to include in the result
                              (e.g., {"author": "author", "qualification": "qualification"}).

        Returns:
            A list of dictionaries containing the parsed fields.
        """
        indexed_keys = [
            key for key in form_data.keys() if key.startswith(field_prefix)
        ]
        index_values = {
            key.split("[")[1].split("]")[0] for key in indexed_keys
        }
        result = []

        for index in sorted(index_values, key=int):
            entry = {
                "en": self._parse_field(
                    form_data, f"{field_prefix}[{index}][en]", default=""
                ),
                "ar": self._parse_field(
                    form_data, f"{field_prefix}[{index}][ar]", default=""
                ),
                "image": self._handle_file_upload(
                    files,
                    f"{field_prefix}[{index}][image]",
                    form_data.get(f"{field_prefix}[{index}][existing_image]"),
                ),
            }

            # Add additional fields if provided
            if additional_fields:
                for field_key, field_name in additional_fields.items():
                    entry[field_key] = self._parse_field(
                        form_data,
                        f"{field_prefix}[{index}][{field_name}]",
                        default="",
                    )

            result.append(entry)

        return result

    def _parse_field(
        self,
        form_data: Dict[str, Any],
        field_name: str,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """Parse a single field from form data."""
        value = form_data.get(field_name)
        return value.strip() if value else default

    def _handle_file_upload(
        self,
        files: Dict[str, Any],
        field_name: str,
        existing_image: Optional[str] = None,
    ) -> Optional[str]:
        """
        Handle file upload and return the saved file path.
        If no new file is uploaded, retain the existing image.
        """
        file = files.get(field_name)
        if file and file.filename:
            return self.handle_file_upload(file)
        return existing_image
