"""
Project Service Module

This module provides the business logic for project-related operations.
"""

import math
from datetime import date
from typing import Any, Dict, List, Optional

from marshmallow import ValidationError
from sqlalchemy import cast, or_

from app.extensions import db
from app.models import Project
from app.schemas.project_schema import ProjectSchema
from utils.file_manager import FileManager


class ProjectService:
    """Project service class."""

    def __init__(self, page_size: int = 3):
        """Initialize project service."""
        self.page_size = page_size
        self.project_schema = ProjectSchema()

    def create_project(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Project | Dict[str, Any]:
        """
        Create a new project.
        Args:
            form_data (Dict[str, Any]): The project data to create.
            files (Dict[str, Any]): The uploaded files.
        Returns:
            Project: The created project instance.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)
            # Validate the data using the schema
            errors = ProjectSchema().validate(processed_data)
            if errors:
                raise ValidationError(errors)
            project = Project()
            project.create(**processed_data)
            return project
        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_project(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Project:
        """
        Update an existing project.

        Args:
            uuid (str): The UUID of the project to update.
            form_data (Dict[str, Any]): The project data to update.
            files (Dict[str, Any]): The uploaded files.

        Returns:
            Optional[Project]: The updated project instance if found, otherwise None.
        """
        try:
            # Process and validate form data
            form_data = self.validate_form_data(form_data, files)

            # Validate project data
            errors = self.project_schema.validate(form_data)
            if errors:
                raise ValidationError(errors)

            project = Project.get_byuuid(uuid)
            if project:
                project.update(**form_data)
            return project
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
        project = Project.get_byuuid(uuid)
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
        project = Project.get_byuuid(uuid)

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
        return Project.get_all_by(author=author)

    def get_all(
        self, status: str = "all", page: int = 1
        ) -> Dict[str, Any]:
        """
        Retrieve all projects with pagination.

        Args:
            page (int): The page number to retrieve (default is 1).
            status (str): The status of the projects to filter by (default is 'all').
            search_str (str): The search string to filter projects by title.

        Returns:
            List[Project]: A list of projects for the specified page.
        """
        pagination = Project.query.filter_by(deleted_at=None)\
                .paginate(page=page, per_page=self.page_size)
        total_pages = math.ceil(pagination._query_count() / self.page_size)
        project_list = [t.to_dict() for t in pagination.items]
        next_page = page + 1 if pagination.has_next else None


        return dict(
            projects=project_list,
            total_pages=total_pages,
            page=page,
            next_page=next_page,
        )

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
        return Project.get_all_by(date_of_completion=date_of_completion)

    def search_projects_by_title(self, title: str) -> List[Project]:
        """
        Search for projects by title.

        Args:
            title (str): The title to search for.

        Returns:
            List[Project]: A list of projects matching the title.
        """
        return Project.query.filter(
            Project.deleted_at.is_(None),
            or_(
                cast(Project.title["en"], db.String).ilike(f"%{title}%"),
                cast(Project.title["ar"], db.String).ilike(f"%{title}%"),
            ),
        ).all()

    def restore_project(self, uuid: str) -> Optional[Project]:
        """
        Restore a soft-deleted project.

        Args:
            uuid (str): The UUID of the project to restore.

        Returns:
            Optional[Project]: The restored project instance if found, otherwise None.
        """
        project = Project.get_byuuid(uuid)
        if project and project.deleted_at:
            project.deleted_at = None
            db.session.commit()
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
                "email": (
                    form_data.get("author[email]").strip()
                    if form_data.get("author[email]")
                    else None
                ),
            },
            "status": form_data.get("status", "ongoing").strip(),
            "date_of_completion": form_data.get("date_of_completion"),
            "tags": {
                "en": self._parse_tags(form_data.get("tags[en]")),
                "ar": self._parse_tags(form_data.get("tags[ar]")),
            },
        }

        # Handle hero_image upload
        hero_image = files.get("hero_image")
        processed_data["hero_image"] = FileManager(hero_image).save()

        # Process content field
        processed_data["content"] = self._parse_indexed_fields(form_data, "content")

        # Process testimonials field
        processed_data["testimonials"] = self._parse_testimonials(form_data)
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
        self, form_data: Dict[str, Any], field_prefix: str
    ) -> List[Dict[str, str]]:
        """Parse indexed fields like content[0][en], content[0][ar]."""
        indexed_keys = [key for key in form_data.keys() if key.startswith(field_prefix)]
        index_values = set([key.split("[")[1].split("]")[0] for key in indexed_keys])
        result = []
        for index in sorted(index_values, key=int):
            entry = {
                "en": (
                    form_data.get(f"{field_prefix}[{index}][en]").strip()
                    if form_data.get(f"{field_prefix}[{index}][en]")
                    else ""
                ),
                "ar": (
                    form_data.get(f"{field_prefix}[{index}][ar]").strip()
                    if form_data.get(f"{field_prefix}[{index}][ar]")
                    else ""
                ),
            }
            result.append(entry)
        return result

    def _parse_testimonials(self, form_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse testimonials fields like testimonials[0][en], testimonials[0][author]."""
        indexed_keys = [
            key for key in form_data.keys() if key.startswith("testimonials")
        ]
        index_values = set([key.split("[")[1].split("]")[0] for key in indexed_keys])
        result = []
        for index in sorted(index_values, key=int):
            entry = {
                "en": (
                    form_data.get(f"testimonials[{index}][en]").strip()
                    if form_data.get(f"testimonials[{index}][en]")
                    else ""
                ),
                "ar": (
                    form_data.get(f"testimonials[{index}][ar]").strip()
                    if form_data.get(f"testimonials[{index}][ar]")
                    else ""
                ),
                "author": (
                    form_data.get(f"testimonials[{index}][author]").strip()
                    if form_data.get(f"testimonials[{index}][author]")
                    else ""
                ),
                "qualification": (
                    form_data.get(f"testimonials[{index}][qualification]").strip()
                    if form_data.get(f"testimonials[{index}][qualification]")
                    else ""
                ),
            }
            result.append(entry)
        return result
