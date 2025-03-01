"""
Team Service Module

This module provides the business logic for team-related operations.
"""

from typing import Any, Dict, List, Optional

from marshmallow import ValidationError

from app.models.team import Team
from app.schemas.team_schema import TeamSchema
from utils.db_utils import search_by_multilang_field
from utils.file_utils import handle_file_upload
from utils.form_utils import parse_key_value_items, parse_nested_field
from utils.service_base import BaseService


class TeamService(BaseService):
    """Team service class."""

    def __init__(self, page_size: int = 10):
        """Initialize team service."""
        super().__init__(Team, TeamSchema, page_size)

    def create_team_member(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Team:
        """Create a new team member."""
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            team_member = Team()
            team_member.create(**processed_data)
            return team_member

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_team_member(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Optional[Team]:
        """Update an existing team member."""
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            team_member = Team.get_byuuid(uuid)
            if team_member:
                team_member.update(**processed_data)
                return team_member

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def search_team_members_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search for team members by name."""
        print("search_team_members_by_name", name)
        return search_by_multilang_field(Team, "name", name)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and validate form data for creating/updating a team member."""
        processed_data = {
            "name": parse_nested_field(form_data, "name"),
            "role": parse_nested_field(form_data, "role"),
            "bio": parse_nested_field(form_data, "bio"),
            "socials": parse_key_value_items(form_data.get("socials")),
        }

        # Handle image upload
        image = files.get("image")
        if image and image.filename:
            processed_data["image"] = handle_file_upload(image)

        return processed_data
