"""
Team Service Module

This module provides the business logic for team-related operations.
"""

import os
from typing import Any, Dict, List, Optional

from flask import current_app
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.team import Team
from app.schemas.team_schema import TeamSchema


class TeamService:
    """Team service class."""

    def __init__(self, page_size: int = 10):
        """Initialize team service."""
        self.page_size = page_size
        self.team_schema = TeamSchema()

    def create_team_member(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Team:
        """
        Create a new team member.

        Args:
            form_data (Dict[str, Any]): The team member data to create.
            files (Dict[str, Any]): The uploaded files.

        Returns:
            Team: The created team member instance.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate the data using the schema
            errors = self.team_schema.validate(processed_data)
            if errors:
                raise ValidationError(errors)

            team_member = Team()
            team_member.create(**processed_data)
            return team_member

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_team_member(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Optional[Team]:
        """
        Update an existing team member.

        Args:
            uuid (str): The UUID of the team member to update.
            form_data (Dict[str, Any]): The team member data to update.
            files (Dict[str, Any]): The uploaded files.

        Returns:
            Optional[Team]: The updated team member instance if found, otherwise None.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate team data
            errors = self.team_schema.validate(processed_data)
            if errors:
                raise ValidationError(errors)

            team_member = Team.get_byuuid(uuid)
            if team_member:
                team_member.update(**processed_data)
                return team_member

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def delete_team_member(self, uuid: str, permanent: bool = False) -> bool:
        """
        Delete a team member.

        Args:
            uuid (str): The UUID of the team member to delete.
            permanent (bool): If True, permanently delete the team member. Otherwise, soft delete.

        Returns:
            bool: True if the team member was deleted, False if the team member was not found.
        """
        team_member = Team.get_byuuid(uuid)
        if team_member:
            team_member.delete(permanent=permanent)
            return True
        return False

    def restore_team_member(self, uuid: str) -> Optional[Team]:
        """
        Restore a soft-deleted team member.

        Args:
            uuid (str): The UUID of the team member to restore.

        Returns:
            Optional[Team]: The restored team member instance if found, otherwise None.
        """
        team_member = Team.get_byuuid(uuid)
        if team_member and team_member.deleted_at:
            team_member.restore()
            return team_member
        return None

    def get_team_member_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a team member by their UUID.

        Args:
            uuid (str): The UUID of the team member to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The team member data if found, otherwise None.
        """
        team_member = Team.get_byuuid(uuid)
        if team_member:
            team_data = team_member.to_dict()
            return team_data
        return None

    def get_all_team_members(self, page: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieve all team members with pagination.

        Args:
            page (int): The page number to retrieve (default is 1).

        Returns:
            List[Dict[str, Any]]: A list of team members for the specified page.
        """
        return [
            t.to_dict()
            for t in Team.query.filter_by(deleted_at=None)
            .paginate(page=page, per_page=self.page_size)
            .items
        ]

    def search_team_members_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Search for team members by name.

        Args:
            name (str): The name to search for.

        Returns:
            List[Dict[str, Any]]: A list of team members matching the name.
        """
        return Team.query.filter(
            Team.deleted_at.is_(None),
            (
                db.cast(Team.name["en"], db.String).ilike(f"%{name}%")
                | db.cast(Team.name["ar"], db.String).ilike(f"%{name}%")
            ),
        ).all()

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and validate form data for creating/updating a team member."""
        processed_data = {
            "name": self._parse_nested_field(form_data, "name"),
            "role": self._parse_nested_field(form_data, "role"),
            "bio": self._parse_nested_field(form_data, "bio"),
            "socials": self._parse_socials(form_data.get("socials")),
        }

        # Handle image upload
        image = files.get("image")
        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            image.save(filepath)
            processed_data["image"] = filepath  # Save file path

        return processed_data

    def _parse_nested_field(
        self, form_data: Dict[str, Any], field_prefix: str
    ) -> Dict[str, str]:
        """Parse nested fields like name[en], name[ar]."""
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

    def _parse_socials(self, socials_str: Optional[str]) -> Dict[str, str]:
        """Parse socials string into a dictionary of key-value pairs."""
        if not socials_str:
            return {}
        socials = {}
        for item in socials_str.split(","):
            key, value = item.split(":")
            socials[key.strip()] = value.strip()
        return socials
