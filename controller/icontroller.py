"""ABC Controller module."""
from abc import ABC, abstractmethod


class IController(ABC):
    """Controller abstract class."""

    @abstractmethod
    def process_entity_get(self, *args, **kwargs):
        """
        GET Entity processing. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """

    @abstractmethod
    def process_entity_post(self, *args, **kwargs):
        """
        POST Entity processing. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """

    @abstractmethod
    def process_get(self, *args, **kwargs):
        """
        GET processing. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """

    @abstractmethod
    def process_post(self, *args, **kwargs):
        """
        POST processing. ABC.

        Args:
            args: parameters
            kwargs: key parameters

        """
