"""
Research Service Module
"""

from typing import Any, Dict, List, Optional

from marshmallow import ValidationError

from app.models import Research
from app.schemas import ResearchSchema
from utils.compose_i18n import compose_i18n
from utils.db_utils import search_by_multilang_field
from utils.form_utils import parse_nested_field
from utils.service_base import BaseService


class ResearchService(BaseService):
    """Research service class."""

    def __init__(self, page_size: int = 10):
        """Initialize research service."""
        super().__init__(Research, ResearchSchema, page_size)

    def create_research(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Research:
        """
        Create a new research entry.

        Args:
            form_data: Dictionary containing research data from the form.
            files: Dictionary containing uploaded files (e.g., hero_image, images).

        Returns:
            The created Research instance.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Create the research entry
            research = self.model_class()
            research.create(**processed_data)
            return research

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update_research(
        self, uuid: str, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Optional[Research]:
        """
        Update an existing research entry.

        Args:
            uuid: The UUID of the research entry to update.
            form_data: Dictionary containing updated research data.
            files: Dictionary containing updated files (e.g., hero_image, images).

        Returns:
            The updated Research instance if found, otherwise None.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            # Process and validate form data
            processed_data = self.validate_form_data(form_data, files)

            # Validate with schema
            self.validate_with_schema(processed_data)

            # Retrieve the research entry by UUID
            research = self.model_class.get_byuuid(uuid)
            if research:
                research.update(**processed_data)
                return research

            return None

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def search_researches_by_title(self, title: str) -> Dict[str, Any]:
        """
        Search for research entries by title.

        Args:
            title: The search term to look for in the title field.

        Returns:
            Dictionary containing search results and pagination metadata.
        """
        return search_by_multilang_field(self.model_class, "title", title)

    def validate_form_data(
        self, form_data: Dict[str, Any], files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process and validate form data for creating/updating a research entry.

        Args:
            form_data: Dictionary containing research data from the form.
            files: Dictionary containing uploaded files (e.g., hero_image, images).

        Returns:
            Processed and validated data dictionary.
        """
        processed_data = {
            "title": parse_nested_field(form_data, "title"),
            "author": {
                "name": parse_nested_field(form_data, "author[name]"),
                "email": (
                    form_data.get("author[email]").strip()
                    if form_data.get("author[email]")
                    else None
                ),
            },
            "tags": {
                "en": self._parse_tags(form_data.get("tags[en]")),
                "ar": self._parse_tags(form_data.get("tags[ar]")),
            },
            "date_of_completion": form_data.get("date_of_completion"),  # Optional field
            "content": compose_i18n(form_data, "content"),  # Optional field
            "testimonials": self._parse_testimonials(form_data),  # Optional field
        }

        # Handle hero_image upload
        hero_image = files.get("hero_image")
        if hero_image and hero_image.filename:
            processed_data["hero_image"] = self.file_manager(hero_image).save()

        # Handle images upload
        images = files.getlist("images") if "images" in files else []
        if images:
            processed_data["images"] = [
                self.file_manager(image).save() for image in images if image.filename
            ]

        return processed_data

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
