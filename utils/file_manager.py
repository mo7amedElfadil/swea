"""Module that provides abstract and concrete file storage implementations."""

import abc
import os
import uuid
from typing import BinaryIO, List, Optional, Set, Tuple

from marshmallow import ValidationError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import Config


class StorageBackend(abc.ABC):
    """Abstract base class for all storage backends."""

    @abc.abstractmethod
    def save_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        directory: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Save a file to the storage backend.

        Args:
            file_obj: The file-like object to save
            filename: The filename to use
            directory: The directory where the file will be saved
            content_type: The MIME type of the file

        Returns:
            The file path or URI that can be used to retrieve the file
        """
        pass

    @abc.abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the storage backend.

        Args:
            file_path: The file path or URI to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in the storage backend.

        Args:
            file_path: The file path or URI to check

        Returns:
            True if the file exists, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_public_url(self, file_path: str) -> str:
        """
        Get a public URL for the file.

        Args:
            file_path: The file path or URI

        Returns:
            A public URL for the file
        """
        pass


class LocalStorageBackend(StorageBackend):
    """Storage backend that saves files to the local filesystem."""

    def __init__(self, base_path: str, base_url: str = "/uploads"):
        """
        Initialize the local storage backend.

        Args:
            base_path: The base directory path where files will be stored
            base_url: The base URL that will be used to construct public URLs
        """
        self.base_path = base_path
        self.base_url = base_url.rstrip("/") + "/"

        # Ensure the directory exists
        os.makedirs(self.base_path, exist_ok=True)

    def save_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        directory: str,
        content_type: Optional[str] = None,
    ) -> str:
        """Save a file to the local filesystem."""
        safe_filename = secure_filename(filename)

        # Create directory if it doesn't exist
        dir_path = os.path.join(self.base_path, directory)
        os.makedirs(dir_path, exist_ok=True)

        # Save file
        file_path = os.path.join(dir_path, safe_filename)

        with open(file_path, "wb") as dest_file:
            file_obj.seek(0)
            dest_file.write(file_obj.read())

        # Return relative path for storage in database
        return os.path.join(directory, safe_filename)

    def delete_file(self, file_path: str) -> bool:
        """Delete a file from the local filesystem."""
        if not file_path:
            return False

        # Convert relative path to absolute path
        absolute_path = os.path.join(self.base_path, file_path)

        if os.path.exists(absolute_path):
            os.remove(absolute_path)
            return True
        return False

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in the local filesystem."""
        if not file_path:
            return False

        # Convert relative path to absolute path
        absolute_path = os.path.join(self.base_path, file_path)
        return os.path.exists(absolute_path)

    def get_public_url(self, file_path: str) -> str:
        """Get a public URL for the file."""
        if not file_path:
            return ""
        return self.base_url + file_path


class S3StorageBackend(StorageBackend):
    """Storage backend that saves files to AWS S3."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """
        Initialize the S3 storage backend.

        Args:
            bucket_name: The S3 bucket name
            aws_access_key_id: AWS access key ID (optional if using instance profile or environment variables)
            aws_secret_access_key: AWS secret access key (optional if using instance profile or environment variables)
            region_name: AWS region name (optional if using default region)
        """
        # Import boto3 here to avoid requiring it for other storage backends
        import boto3

        self.bucket_name = bucket_name

        # Initialize S3 client
        session_kwargs = {}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key
        if region_name:
            session_kwargs["region_name"] = region_name

        self.s3_client = boto3.session.Session(**session_kwargs).client("s3")

        # Define the base URL pattern for this bucket and region
        if region_name and region_name != "us-east-1":
            self.base_url = (
                f"https://{bucket_name}.s3.{region_name}.amazonaws.com/"
            )
        else:
            self.base_url = f"https://{bucket_name}.s3.amazonaws.com/"

    def save_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        directory: str,
        content_type: Optional[str] = None,
    ) -> str:
        """Save a file to S3."""
        safe_filename = secure_filename(filename)

        # Define the S3 key (path within bucket)
        s3_key = f"{directory}/{safe_filename}"

        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        self.s3_client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=self.bucket_name,
            Key=s3_key,
            ExtraArgs=extra_args,
        )

        # Return the path for storage in database
        return s3_key

    def delete_file(self, file_path: str) -> bool:
        """Delete a file from S3."""
        if not file_path:
            return False

        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name, Key=file_path
            )
            return True
        except Exception:
            return False

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in S3."""
        if not file_path:
            return False

        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except Exception:
            return False

    def get_public_url(self, file_path: str) -> str:
        """Get a public URL for the file."""
        if not file_path:
            return ""
        return self.base_url + file_path


class FileValidator:
    """Validates files based on various criteria."""

    def __init__(
        self,
        allowed_extensions: Optional[Set[str]] = None,
        max_size_bytes: Optional[int] = None,
        allowed_mime_types: Optional[Set[str]] = None,
    ):
        """
        Initialize the file validator.

        Args:
            allowed_extensions: Set of allowed file extensions (lowercase, without dot)
            max_size_bytes: Maximum allowed file size in bytes
            allowed_mime_types: Set of allowed MIME types
        """
        self.allowed_extensions = allowed_extensions
        self.max_size_bytes = max_size_bytes
        self.allowed_mime_types = allowed_mime_types

    def validate(self, file: FileStorage) -> Tuple[bool, List[str]]:
        """
        Validate a file against the configured criteria.

        Args:
            file: The file to validate

        Returns:
            A tuple of (is_valid, error_messages)
        """
        errors = []

        if not file or not file.filename:
            return False, ["No file provided or empty filename"]

        # Check file extension
        if self.allowed_extensions:
            ext = (
                file.filename.rsplit(".", 1)[-1].lower()
                if "." in file.filename
                else ""
            )
            if ext not in self.allowed_extensions:
                extensions_list = ", ".join(self.allowed_extensions)
                errors.append(
                    f"Invalid file extension. Allowed extensions: {extensions_list}"
                )

        # Check file size
        if self.max_size_bytes:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)  # Reset file pointer
            if size > self.max_size_bytes:
                max_mb = self.max_size_bytes / (1024 * 1024)
                errors.append(f"File too large. Maximum size: {max_mb:.1f} MB")

        # Check MIME type
        if (
            self.allowed_mime_types
            and file.content_type not in self.allowed_mime_types
        ):
            mime_types_list = ", ".join(self.allowed_mime_types)
            errors.append(
                f"Invalid file type. Allowed types: {mime_types_list}"
            )

        return len(errors) == 0, errors


class FileManager:
    """
    High-level file management service that handles uploading, validating, and storing files.

    This class serves as a facade for the underlying storage system and validates files
    before storing them.
    """

    DEFAULT_VALIDATORS = {
        "image": FileValidator(
            allowed_extensions=Config.ALLOWED_IMAGES_EXTENSIONS,
            max_size_bytes=10 * 1024 * 1024,  # 10 MB
            allowed_mime_types={
                "image/png",
                "image/jpeg",
                "image/gif",
                "image/webp",
            },
        ),
        "document": FileValidator(
            allowed_extensions=Config.ALLOWED_FILES_EXTENSIONS,
            max_size_bytes=10 * 1024 * 1024,  # 10 MB
            allowed_mime_types={
                "text/plain",
                "application/pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            },
        ),
    }

    def __init__(self, storage_backend: StorageBackend, directory: str = ""):
        """
        Initialize the file manager.

        Args:
            storage_backend: The storage backend to use
            directory: The subdirectory to save files in (usually the model's table name)
        """
        self.storage_backend = storage_backend
        self.directory = directory

    def get_validator_for_file(
        self, file: FileStorage
    ) -> Optional[FileValidator]:
        """
        Determine the appropriate validator based on file extension or MIME type.

        Args:
            file: The file to be validated.

        Returns:
            The appropriate FileValidator instance, or None if no match is found.
        """
        if not file or not file.filename:
            return None  # No file provided

        ext = (
            file.filename.rsplit(".", 1)[-1].lower()
            if "." in file.filename
            else ""
        )
        mime_type = file.content_type

        for _, validator in self.DEFAULT_VALIDATORS.items():
            if (
                validator.allowed_extensions
                and ext in validator.allowed_extensions
            ) or (
                validator.allowed_mime_types
                and mime_type in validator.allowed_mime_types
            ):
                return validator

        return None  # Default case: no specific validator

    def save_file(self, file: FileStorage) -> str:
        """
        Validate and save a file.

        Args:
            file: The file to save.

        Returns:
            The file path or URI.

        Raises:
            ValidationError: If file validation fails.
        """
        validator = self.get_validator_for_file(file)
        if validator:
            is_valid, errors = validator.validate(file)
            if not is_valid:
                raise ValidationError({"file": errors})

        # Generate a unique filename to avoid collisions
        if file.filename:
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

            # Save the file to the storage backend
            return self.storage_backend.save_file(
                file_obj=file.stream,
                filename=unique_filename,
                directory=self.directory,
                content_type=file.content_type,
            )

        raise ValidationError({"file": ["Invalid or empty file"]})

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.

        Args:
            file_path: The file path or URI to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        return self.storage_backend.delete_file(file_path)

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: The file path or URI to check

        Returns:
            True if the file exists, False otherwise
        """
        return self.storage_backend.file_exists(file_path)

    def get_public_url(self, file_path: str) -> str:
        """
        Get a public URL for the file.

        Args:
            file_path: The file path or URI

        Returns:
            A public URL for the file
        """
        return self.storage_backend.get_public_url(file_path)


# Factory function to create a FileManager with the appropriate backend
def create_file_manager(
    storage_type: str = Config.STORAGE_TYPE, directory: str = "", **kwargs
) -> FileManager:
    """
    Create a FileManager with the specified storage backend.

    Args:
        storage_type: The type of storage backend to use ('local' or 's3')
        directory: The subdirectory to save files in (usually the model's table name)
        **kwargs: Additional arguments to pass to the storage backend constructor

    Returns:
        A configured FileManager instance

    Raises:
        ValueError: If the specified storage type is invalid
    """
    if storage_type == "local":
        backend = LocalStorageBackend(
            base_path=kwargs.get("base_path", Config.UPLOAD_FOLDER),
            base_url=kwargs.get("base_url", "/uploads/"),
        )
    elif storage_type == "s3":
        backend = S3StorageBackend(
            bucket_name=Config.S3_BUCKET,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.S3_REGION,
        )
    else:
        raise ValueError(f"Invalid storage type: {storage_type}")

    # Create and return the FileManager instance
    return FileManager(backend, directory)
