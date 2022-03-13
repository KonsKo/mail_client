"""Letter views."""
import logging

from db.schema import Letter
from middleware import require_login
from service.letter_service import LetterService

from filter.letter_filter import LetterAlchemyFilter
from view.base_view import BaseEntityView, BaseManyView

logger = logging.getLogger(__name__)


@require_login
class LetterEntityView(BaseEntityView):
    """Letter view."""

    _tabel = Letter
    _service = LetterService
    _filter = LetterAlchemyFilter


@require_login
class LetterManyView(BaseManyView):
    """Letter view."""

    _tabel = Letter
    _service = LetterService
    _filter = LetterAlchemyFilter
