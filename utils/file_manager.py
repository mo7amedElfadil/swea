"""Module defines file manager class for file operations."""

import os

from marshmallow import ValidationError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import Config


class FileManager:
    """FileManager class for file operations."""

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    def __init__(self, file: FileStorage | None = None):
        """Initialize FileManager class."""
        if file and file.filename:
            ext = file.filename.rsplit(".", 1)[1].lower()
            if not ext or ext not in self.ALLOWED_EXTENSIONS:
                raise ValidationError(
                    {"image": "Invalid file type. Only images are allowed."}
                )
        self.file = file

    def save(self) -> str:
        """Save the file.
        Returns:
          the relative path of the saved file.
        """
        if self.file and self.file.filename:
            filename = secure_filename(self.file.filename)
            filename = f"{os.urandom(8).hex()}_{filename}"

            # Construct the relative URL
            relative_path = os.path.join("uploads", filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            self.file.save(filepath)
            return relative_path
        return ""
