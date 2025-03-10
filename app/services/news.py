"""
News Service Module

This module provides the business logic for news-related operations.
"""
import math
from datetime import date
from typing import Any, Dict, List, Optional

from marshmallow import ValidationError
from sqlalchemy import cast, or_

from app.extensions import db
from app.models import News
from app.schemas.news_schema import NewsSchema
from utils.compose_i18n import compose_i18n
from utils.file_manager import FileManager
from utils.service_base import BaseService

class NewsService(BaseService):
    """News service class."""

    def __init__(self, page_size: int = 3):
        """Initialize news service."""
        self.page_size = page_size
        self.news_schema = NewsSchema()
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
          file = FileManager(form_data.get("image"))
          relative_path = file.save()
          processed_data["image"] = relative_path
          # Validate the data using the schema
          errors = self.news_schema.validate(processed_data)
          if errors:
              raise ValidationError(errors)

          news = News()
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
        news = News.query.filter_by(uuid=uuid).first()
        if not news:
            return None

        try:
            # Process and validate form data
            processed_data = dict(
                title=compose_i18n(form_data, "title"),
                date=form_data.get("date"),
                description=compose_i18n(form_data, "description"),
            )
            if form_data.get("image"):
                processed_data["image"] = form_data.get("image")
                file = FileManager(form_data.get("image"))
                relative_path = file.save()
                processed_data["image"] = relative_path

            # Validate the data using the schema
            errors = self.news_schema.validate(processed_data)
            if errors:
                raise ValidationError(errors)

            news.update(**processed_data)
            return news.to_dict()

        except ValidationError as error:
            raise ValidationError(error.messages) from error

    def delete(self, uuid: str, permanent: bool = False) -> bool:
      """ Delete a news. """
      news_item = News.get_byuuid(uuid)
      if news_item:
          news_item.delete(permanent=permanent)
          return True
      return False

    def search_news(self, query: str) -> List[Dict[str, Any]]:
        """Search news by title or description."""
        news_list = [
            t.to_dict()
            for t in News.query.filter(
                or_(
                    cast(News.title, db.String).ilike(f"%{query}%"),
                    cast(News.description, db.String).ilike(f"%{query}%"),
                )
            )
        ]
        return news_list
