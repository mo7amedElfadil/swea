import os
import uuid

from flask import current_app
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename: str, allowed_extensions=None) -> bool:
    """Check if the file extension is allowed."""
    extensions = allowed_extensions or ALLOWED_EXTENSIONS
    return "." in filename and filename.rsplit(".", 1)[1].lower() in extensions


def handle_file_upload(file, upload_folder=None) -> str | None:
    """
    Process file upload and return the relative path to the saved file.

    Args:
        file: The uploaded file object
        upload_folder: Optional custom upload folder path

    Returns:
        str: Relative path to the saved file

    Raises:
        ValidationError: If file type is invalid
    """
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        raise ValidationError(
            f"Invalid file type. Only {', '.join(ALLOWED_EXTENSIONS)} are allowed."
        )

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"

    # Use default upload folder if none specified
    folder = upload_folder or current_app.config["UPLOAD_FOLDER"]

    # Construct paths
    relative_path = os.path.join("uploads", unique_filename)
    filepath = os.path.join(folder, unique_filename)

    # Save the file
    file.save(filepath)
    return relative_path
