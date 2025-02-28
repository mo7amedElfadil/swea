"""
News Service Module

This module provides the business logic for news-related operations.
"""

import os
from datetime import date
from typing import Any, Dict, List, Optional

from marshmallow import ValidationError
from sqlalchemy import cast, or_
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import News
from app.schemas.news_schema import NewsSchema


class NewsService:
    """News service class."""

    def __init__(self, page_size: int = 10):
        """Initialize news service."""
        self.page_size = page_size
        self.project_schema = NewsSchema()

    def create(self, form_data: Dict[str, Any]) -> News:
      """
      Create a new news.

      Args:
          form_data (Dict[str, Any]): The news data to create.

      Returns:
          News: The created news instance.
      """
      try:
          # Validate the data using the schema
          errors = self.project_schema.validate(form_data)
          if errors:
              raise ValidationError(errors)

          news = News()
          news.create(**form_data)
          return news

      except ValidationError as error:
          raise ValidationError(error.messages) from error
