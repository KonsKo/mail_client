"""ABC Service module."""
from abc import ABC, abstractmethod


class IService(ABC):
    """ABC service class."""

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Init service.

        Args:
            args: arguments
            kwargs: key arguments

        """

    @abstractmethod
    async def create(self, *args, **kwargs):
        """
        Create data.

        Args:
            args: arguments
            kwargs: key arguments

        """

    @abstractmethod
    async def update(self, *args, **kwargs):
        """
        Update data.

        Args:
            args: arguments
            kwargs: key arguments

        """

    @abstractmethod
    async def delete(self, *args, **kwargs):
        """
        Delete data.

        Args:
            args: arguments
            kwargs: key arguments

        """

    @abstractmethod
    async def retrieve(self, *args, **kwargs):
        """
        Retrieve data.

        Args:
            args: arguments
            kwargs: key arguments

        """

    @abstractmethod
    async def send_email(self, *args, **kwargs):
        """
        Send email.

        Args:
            args: arguments
            kwargs: key arguments

        """