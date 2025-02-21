"""Import all models to ensure they are registered with SQLAlchemy."""

from app.models.contact import Contact
from app.models.course import Course, CourseMember
from app.models.member import Member
from app.models.news import News
from app.models.podcast import Podcast, PodcastMember
from app.models.project import Project
from app.models.research import Research
from app.models.team import Team
from app.models.user import User
