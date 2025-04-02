import os
from uuid import uuid4

from werkzeug.utils import secure_filename

from config import Config

# Allowed file extensions

ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS


class ImageProcessing:
    """Class to handle image processing"""

    def allowed_file(self, filename):
        """Check if the file extension is allowed"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    def save_image(self, file, category, identifier):
        """Save an image to the appropriate category folder
        image is saved as uuid.ext

        """
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit(".", 1)[1].lower()
            unique_filename = f"{identifier}.{file_ext}"
            print(Config.UPLOAD_FOLDER)
            file_path = os.path.join(
                Config.UPLOAD_FOLDER, category, unique_filename
            )
            print(file_path)

            file.save(file_path)
            return f"uploads/{category}/{unique_filename}"
        return None

    # pass in the category and the file from request.files
    def upload_image(self, category, file):
        """Upload an image and save it to the appropriate category folder"""
        if category not in Config.UPLOAD_DIRS:
            return None

        uuid = uuid4()
        saved_path = self.save_image(file, category, uuid)
        return saved_path

    def get_image(self, image_path):
        """Get the image path"""
        return image_path
