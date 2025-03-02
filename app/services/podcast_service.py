from typing import Any, Dict, List, Optional

from marshmallow import ValidationError

from app.models.member import Member
from app.models.podcast import Podcast
from app.schemas.podcast_schema import PodcastSchema
from utils.db_utils import search_by_multilang_field
from utils.file_manager import FileManager
from utils.form_utils import parse_nested_field, parse_tags
from utils.service_base import BaseService


class PodcastService(BaseService):
    """Podcast service class."""

    def __init__(self, page_size: int = 10):
        """Initialize podcast service."""
        super().__init__(Podcast, PodcastSchema, page_size)

    def create_podcast(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Podcast:
        """Create a new podcast."""
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            podcast = Podcast()
            podcast.create(**processed_data)

            # Handle members association
            member_uuids = form_data.get("members", [])
            self._associate_members(podcast, member_uuids)

            return podcast

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_podcast(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Optional[Podcast]:
        """Update an existing podcast."""
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            podcast = Podcast.get_byuuid(uuid)
            if podcast:
                podcast.update(**processed_data)

                # Handle members association
                member_uuids = form_data.get("members", [])
                self._associate_members(podcast, member_uuids)

                return podcast

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def search_podcasts_by_title(self, title: str) -> List[Dict[str, Any]]:
        """Search for podcasts by title."""
        return search_by_multilang_field(Podcast, "title", title)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and validate form data for creating/updating a podcast."""
        processed_data = {
            "title": parse_nested_field(form_data, "title"),
            "podcast_name": parse_nested_field(form_data, "podcast_name"),
            "description": parse_nested_field(form_data, "description"),
            "tags": parse_tags(form_data.get("tags")),
            "date": form_data.get("date"),
            "url": form_data.get("url"),
        }

        # Handle image upload
        image = files.get("image")
        if image and image.filename:
            processed_data["image"] = FileManager(image).save()

        return processed_data

    def _associate_members(self, podcast: Podcast, member_uuids: List[str]):
        """Associate members with a podcast."""
        podcast.members.clear()
        for member_uuid in member_uuids:
            member = Member.get_byuuid(member_uuid)
            if member:
                podcast.members.append(member)
