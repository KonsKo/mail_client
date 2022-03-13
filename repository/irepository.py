"""ABC Repository module."""
from abc import ABC, abstractmethod


class IRepository(ABC):
    """Repository abstract class."""

    @abstractmethod
    def insert(self, *args, **kwargs):
        """
        Insert data. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """

    @abstractmethod
    def update(self, *args, **kwargs):
        """
        Update data. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """

    @abstractmethod
    def delete(self, *args, **kwargs):
        """
        Delete data. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """

    @abstractmethod
    def select(self, *args, **kwargs):
        """
        Select ALL data. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """

    @abstractmethod
    def select_first(self, *args, **kwargs):
        """
        Select FIRST data. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """
