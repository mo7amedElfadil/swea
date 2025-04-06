"""
News Service Module

This module provides the business logic for news-related operations.
"""

from typing import Any, Dict, List, Optional

from marshmallow import ValidationError
from sqlalchemy import cast, or_

from app.extensions import db
from app.models import News
from app.schemas import NewsSchema
from utils.compose_i18n import compose_i18n
from utils.service_base import BaseService


class NewsService(BaseService):
    """News service class."""

    def __init__(self, page_size: int = 3):
        """Initialize news service."""
        super().__init__(News, NewsSchema, page_size)

    def create(self, form_data: Dict[str, Any]) -> News:
        """
        Create a new news.

        Args:
            form_data: The news data to create.

        Returns:
            News: The created news instance.
        """
        try:
            # Process and validate form data
            processed_data = dict(
                title=compose_i18n(form_data, "title"),
                date=form_data.get("date"),
                image=form_data.get("image"),
                description=compose_i18n(form_data, "description"),
            )

            image = processed_data.get("image")
            if image and image.filename:
                processed_data["image"] = self.handle_file_upload(image)

            # Validate the data using the schema
            self.validate_with_schema(processed_data)

            news = self.model_class()
            news.create(**processed_data)
            return news

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def update(self, uuid: str, form_data: Dict[str, Any]) -> Optional[News]:
        """
        Update a news.

        Args:
            uuid: The news UUID.
            form_data: The news data to update.

        Returns:
            Optional[News]: The updated news instance.
        """
        news = self.model_class.query.filter_by(uuid=uuid).first()
        if not news:
            return None

        try:
            # Process and validate form data
            processed_data = dict(
                title=compose_i18n(form_data, "title"),
                date=form_data.get("date"),
                image=form_data.get("image"),
                description=compose_i18n(form_data, "description"),
            )

            image = processed_data.get("image")
            if image and image.filename:
                processed_data["image"] = self.handle_file_upload(image)

            # Validate the data using the schema
            self.validate_with_schema(processed_data)

            news.update(**processed_data)
            return news.to_dict()

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def delete(self, uuid: str, permanent: bool = False) -> bool:
        """Delete a news."""
        news_item = self.model_class.get_byuuid(uuid)
        if news_item:
            news_item.delete(permanent=permanent)
            self.file_manager.delete_file(news_item.image)
            return True
        return False

    def search_news(self, query: str) -> List[Dict[str, Any]]:
        """Search news by title or description."""
        news_list = [
            t.to_dict()
            for t in self.model_class.query.filter(
                or_(
                    cast(self.model_class.title, db.String).ilike(
                        f"%{query}%"
                    ),
                    cast(self.model_class.description, db.String).ilike(
                        f"%{query}%"
                    ),
                )
            )
        ]
        return news_list
