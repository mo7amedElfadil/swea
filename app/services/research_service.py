from typing import Any, Dict, Optional

from marshmallow import ValidationError

from app.models.research import Research
from app.schemas.research_schema import ResearchSchema
from utils.db_utils import search_by_multilang_field
from utils.file_manager import FileManager
from utils.form_utils import parse_nested_field, parse_tags
from utils.service_base import BaseService


class ResearchService(BaseService):
    """Research service class."""

    def __init__(self, page_size: int = 10):
        """Initialize research service."""
        super().__init__(Research, ResearchSchema, page_size)

    def create_research(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Research:
        """Create a new research."""
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            research = Research()
            research.create(**processed_data)

            return research

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_research(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Optional[Research]:
        """Update an existing research."""
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            research = Research.get_byuuid(uuid)
            if research:
                research.update(**processed_data)

                return research
        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def search_research(self, title: str) -> Dict[str, Any]:
        """Search research by title."""
        return search_by_multilang_field(Research, "title", title)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and process form data."""
        processed_data = {
            "title": parse_nested_field(form_data, "title"),
            "author": parse_nested_field(form_data, "author"),
            "date_of_completion": form_data.get("date_of_completion"),
            "content": parse_nested_field(form_data, "content"),
            "tags": parse_tags(form_data.get("tags", {})),
            "testimonials": parse_nested_field(form_data, "testimonials"),
        }

        processed_data["hero_image"] = FileManager(files.get("hero_image")).save()
        processed_data["images"] = [
            FileManager(image).save() for image in files.get("images", [])
        ]

        return processed_data
