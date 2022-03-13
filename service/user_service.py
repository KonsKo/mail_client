"""User service module."""
from db.schema import User
from repository.base_repository import BaseRepository

from service.base_service import BaseService


class UserService(BaseService):
    """User service."""

    table = User
    repo = BaseRepository
