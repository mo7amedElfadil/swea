"""
Project Service Module

This module provides the business logic for project-related operations.
"""

import os
import re
from datetime import date
from typing import Any, Dict, List, Optional

from flask import current_app
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Project
from app.schemas.project_schema import ProjectSchema


class ProjectService:
    """Project service class."""

    def __init__(self, page_size: int = 10):
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
            form_data = self.validate_form_data(form_data, files)

            # Validate the data using the schema
            errors = ProjectSchema().validate(form_data)
            if errors:
                raise ValidationError(errors)

            project = Project()
            project.create(**form_data)
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

            print("=====PROJECT DATA=====", project_data)

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

    def get_all_projects(self, page: int = 1) -> List[Project]:
        """
        Retrieve all projects with pagination.

        Args:
            page (int): The page number to retrieve (default is 1).

        Returns:
            List[Project]: A list of projects for the specified page.
        """
        return [
            p.to_dict()
            for p in (
                Project.query.filter_by(deleted_at=None)
                .paginate(page=page, per_page=self.page_size)
                .items
            )
        ]

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
            Project.title.contains(title), Project.deleted_at.is_(None)
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

        print("==TESTIMONIALS===>", form_data.get("testimonials"))

        processed_data = {
            "title": {
                "en": form_data.get("title[en]"),
                "ar": form_data.get("title[ar]"),
            },
            "author": {
                "name": {
                    "en": form_data.get("author[name][en]"),
                    "ar": form_data.get("author[name][ar]"),
                },
                "email": form_data.get("author[email]"),
            },
            "status": form_data.get("status", "ongoing"),
            "date_of_completion": form_data.get("date_of_completion"),
            "tags": {
                "en": (
                    form_data.get("tags[en]", "").split(",")
                    if form_data.get("tags[en]")
                    else []
                ),
                "ar": (
                    form_data.get("tags[ar]", "").split(",")
                    if form_data.get("tags[ar]")
                    else []
                ),
            },
            "testimonials": {
                "en": (
                    [
                        t.strip()
                        for t in form_data.get("testimonials[en]", "").split(",")
                        if t.strip()
                    ]
                    if form_data.get("testimonials[en]")
                    else []
                ),
                "ar": (
                    [
                        t.strip()
                        for t in form_data.get("testimonials[ar]", "").split(",")
                        if t.strip()
                    ]
                    if form_data.get("testimonials[ar]")
                    else []
                ),
            },
        }

        # Handle hero_image upload
        hero_image = files.get("hero_image")
        if hero_image and hero_image.filename:
            filename = secure_filename(hero_image.filename)
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            hero_image.save(filepath)
            processed_data["hero_image"] = filepath  # Save file path

        # Handle multiple images upload
        images = files.get("images", [])  # Use getlist() for multiple files
        image_paths = []
        for image in images:
            if image.filename:
                filename = secure_filename(image.filename)
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                image.save(filepath)
                image_paths.append(filepath)
        processed_data["images"] = image_paths  # Save file paths list

        # Process content field
        content = []
        content_keys = [key for key in form_data.keys() if key.startswith("content")]

        index_values = set([key.split("[")[1].split("]")[0] for key in content_keys])
        # Build content list
        for index in index_values:
            en_key = f"content[{index}][en]"
            ar_key = f"content[{index}][ar]"
            content_entry = {
                "en": form_data.get(en_key),
                "ar": form_data.get(ar_key),
            }
            content.append(content_entry)

        processed_data["content"] = content

        return processed_data
