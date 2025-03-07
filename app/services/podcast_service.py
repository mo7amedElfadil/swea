"""
Podcast Service Module
"""

from typing import Any, Dict, List, Optional

from marshmallow import ValidationError

from app.models.podcast import Podcast, PodcastMember
from app.schemas.podcast_schema import PodcastSchema
from utils.db_utils import search_by_multilang_field
from utils.file_manager import FileManager
from utils.form_utils import parse_key_value_items, parse_nested_field
from utils.service_base import BaseService


class PodcastService(BaseService):
    """Podcast service class."""

    def __init__(self, page_size: int = 10):
        """Initialize podcast service."""
        super().__init__(Podcast, PodcastSchema, page_size)

    def create_podcast(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Podcast:
        """
        Create a new podcast.

        Args:
            form_data: Dictionary containing podcast data from the form.
            files: Dictionary containing uploaded files (e.g., image).

        Returns:
            The created Podcast instance.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Create the podcast
            podcast = Podcast()
            podcast.create(**processed_data)
            return podcast

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_podcast(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Optional[Podcast]:
        """
        Update an existing podcast.

        Args:
            uuid: The UUID of the podcast to update.
            form_data: Dictionary containing updated podcast data.
            files: Dictionary containing updated files (e.g., image).

        Returns:
            The updated Podcast instance if found, otherwise None.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Retrieve the podcast by UUID
            podcast = Podcast.get_byuuid(uuid)
            if podcast:
                podcast.update(**processed_data)
                return podcast

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def add_members_to_podcast(
        self, podcast_uuid: str, member_uuids: List[str]
    ) -> bool:
        """
        Add members to a podcast.

        Args:
            podcast_uuid: The UUID of the podcast.
            member_uuids: List of UUIDs of members to add.

        Returns:
            True if members were successfully added, False otherwise.
        """
        podcast = Podcast.get_byuuid(podcast_uuid)
        if not podcast:
            return False

        # Add members to the podcast
        for member_uuid in member_uuids:
            podcast_member = PodcastMember(
                podcast_uuid=podcast_uuid, member_uuid=member_uuid
            )
            podcast_member.create()

        return True

    def remove_members_from_podcast(
        self, podcast_uuid: str, member_uuids: List[str]
    ) -> bool:
        """
        Remove members from a podcast.

        Args:
            podcast_uuid: The UUID of the podcast.
            member_uuids: List of UUIDs of members to remove.

        Returns:
            True if members were successfully removed, False otherwise.
        """
        podcast = Podcast.get_byuuid(podcast_uuid)
        if not podcast:
            return False

        # Remove members from the podcast
        for member_uuid in member_uuids:
            podcast_member = PodcastMember.query.filter_by(
                podcast_uuid=podcast_uuid, member_uuid=member_uuid
            ).first()
            if podcast_member:
                podcast_member.delete(permanent=True)

        return True

    def search_podcasts_by_title(self, title: str) -> Dict[str, Any]:
        """
        Search for podcasts by title.

        Args:
            title: The search term to look for in the title field.

        Returns:
            Dictionary containing search results and pagination metadata.
        """
        return search_by_multilang_field(Podcast, "title", title)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process and validate form data for creating/updating a podcast.

        Args:
            form_data: Dictionary containing podcast data from the form.
            files: Dictionary containing uploaded files (e.g., image).

        Returns:
            Processed and validated data dictionary.
        """
        processed_data = {
            "title": parse_nested_field(form_data, "title"),
            "podcast_name": parse_nested_field(form_data, "podcast_name"),
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
