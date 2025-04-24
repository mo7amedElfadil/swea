"""configuration file for your Flask application."""

from os import getenv
from pathlib import Path
from typing import Final, List

import redis
from dotenv import load_dotenv
from git import InvalidGitRepositoryError, Repo

# Base directory
BASE_DIR: Final[Path] = Path(__file__).parent.resolve()

load_dotenv()


class Config:
    """Configuration class for the Flask application."""

    # Translation configuration
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"
    BABEL_SUPPORTED_LOCALES = ["en", "ar"]
    BABEL_TRANSLATION_DIRECTORIES = str(BASE_DIR / "app/translations")

    # Settings for storage backends
    STORAGE_TYPE = getenv("STORAGE_TYPE", "local")  # local or s3
    S3_BUCKET = "swea-bucket-name"
    S3_REGION = "us-east-1"
    AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
    AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")

    # Upload directories to create
    UPLOAD_DIRS: Final[List[str]] = [
        "projects",
        "research",
        "courses",
        "podcasts",
        "news",
        "teams",
        "users",
        "members",
    ]

    # Determine upload folder path
    _upload_dir_env = getenv("UPLOAD_FOLDER", "./uploads/")
    UPLOAD_FOLDER: Final[Path] = (BASE_DIR / _upload_dir_env).resolve()

    # Create upload directories
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    for directory in UPLOAD_DIRS:
        (UPLOAD_FOLDER / directory).mkdir(exist_ok=True)

    # Allowed file extensions
    ALLOWED_IMAGES_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_FILES_EXTENSIONS = {"pdf", "docx", "pptx", "xlsx", "txt"}

    # Application configuration
    PREFERRED_URL_SCHEME = getenv("PREFERRED_URL_SCHEME", "https")
    API_KEY = getenv("API_KEY", "you-will-never-guess")
    SECURITY_PASSWORD_SALT = getenv(
        "SECURITY_PASSWORD_SALT", "you-will-never-guess"
    )
    DEBUG = int(getenv("FLASK_DEBUG", 0))
    BASE_URL = (
        getenv("DEV_BASE_URL") if DEBUG == 1 else getenv("PRODUCTION_BASE_URL")
    )

    # Flask session configuration
    SECRET_KEY = getenv("SECRET_KEY", "you-will-never-guess")
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(getenv("SESSION_REDIS_URL"))
    SESSION_COOKIE_NAME = "swea_admin"
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True

    # Email configuration
    SMTP_HOST = getenv("SMTP_HOST")
    SMTP_PORT = int(getenv("SMTP_PORT", "587"))
    SMTP_USER = getenv("SMTP_USER")
    SMTP_PASS = getenv("SMTP_PASS")

    # Redis Database configuration for queue service
    REDIS_URL = getenv("REDIS_URL")
    TOKEN_REDIS_URL = getenv("TOKEN_REDIS_URL")
    LIMITER_REDIS_URL = getenv("LIMITER_REDIS_URL")

    # Database configuration (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = getenv(
        "POSTGRES_URL", "postgresql://swea_user:swea_pass@localhost/swea_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask cache Configuration
    if DEBUG == 1:
        CACHE_TYPE = "null"
    else:
        CACHE_TYPE = "redis"

    CACHE_REDIS_URL = getenv("CACHE_REDIS_URL")
    CACHE_KEY_PREFIX = "swea_"
    CACHE_DEFAULT_TIMEOUT = 86400  # 1 day

    @staticmethod
    def get_git_commit_hash():
        """Get the short hash of the latest git commit."""
        try:
            repo = Repo(Path(__file__).resolve().parent)
            return repo.head.commit.hexsha[:7]
        except (InvalidGitRepositoryError, Exception):
            return "dev"

    CACHE_VERSION = get_git_commit_hash.__func__()

    # Rate limiter configuration
    RATE_LIMITS = {
        "DEFAULT": ["200 per day", "50 per hour"],
        "STRICT": ["5 per minute", "20 per hour"],
        "NORMAL": ["10 per minute", "100 per hour"],
        "LENIENT": ["30 per minute", "300 per hour"],
        "API": ["60 per minute", "1000 per hour"],
    }

    # Email validation configuration
    DISPOSABLE_EMAIL_FILE = "utils/disposable_email_blocklist.conf"

    # Admin credentials
    ADMIN_USERNAME = getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = getenv("ADMIN_PASSWORD", "admin")
