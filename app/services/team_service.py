"""
Team Service Module

This module provides the business logic for team-related operations.
"""

from typing import Any, Dict, Optional

from marshmallow import ValidationError

from app.models import Team
from app.schemas import TeamSchema
from utils.db_utils import search_by_multilang_field
from utils.form_utils import parse_nested_field
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

            # validate the uniqueness of team member order
            existing_team_member = self.model_class.get_by(
                order=processed_data["order"]
            )

            if existing_team_member:
                self.update_team_member_order(
                    order=processed_data["order"], mode=1
                )

            team_member = self.model_class()
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

            # validate the uniqueness of team member order
            existing_team_member = self.model_class.get_by(
                order=processed_data["order"]
            )

            if existing_team_member and existing_team_member.uuid != uuid:
                self.update_team_member_order(
                    order=processed_data["order"],
                    mode=0,
                    limit=existing_team_member.order,
                )

            team_member = self.model_class.get_byuuid(uuid)
            if team_member:
                team_member.update(**processed_data)
                return team_member

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def search_team_members_by_name(self, name: str) -> Dict[str, Any]:
        """Search for team members by name."""
        return search_by_multilang_field(self.model_class, "name", name)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and validate form data for creating/updating a team member."""
        # Parse socials
        socials = {}
        for key, value in form_data.items():
            if key.startswith("socials[") and key.endswith("]"):
                platform = key[len("socials[") : -1]
                if value:  # Only add non-empty values
                    socials[platform] = value

        # Process form data
        processed_data = {
            "name": parse_nested_field(form_data, "name"),
            "role": parse_nested_field(form_data, "role"),
            "bio": parse_nested_field(form_data, "bio"),
            "socials": socials,
            "order": int(form_data.get("order", 1)),
            "email": form_data.get("email"),
        }

        # Handle image upload
        image = files.get("image")
        if image and image.filename:
            processed_data["image"] = self.handle_file_upload(image)

        return processed_data

    def update_team_member_order(
        self, order: int, mode: int, limit: Optional[int] = 0
    ) -> Optional[Team]:
        """
        Cascade update the order of a team member on create/update team member.

        :param order: The order of the team member.
        :param mode: The mode of the order (1 for increase, -1 for decrease).
        :return: The updated team member or None if not found.
        """
        team_member = self.model_class.get_by(order=order)
        if team_member:
            if mode == 1 and limit:
                if team_member.order > limit:
                    team_member.order += 1
            elif mode == -1:
                team_member.order -= 1
            team_member.update()
            self.update_team_member_order(order + 1, mode)
            return team_member

        return None
