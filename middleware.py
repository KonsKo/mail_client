"""Custom middleware module."""

from typing import Awaitable, Callable

from aiohttp import web

from auth.policy import get_current_user_id

_WebHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]


def require_login(func: _WebHandler) -> _WebHandler:
    """
    Decorate login required handlers.

    Args:
        func (_WebHandler): handler to decorate

    Returns:
        func (_WebHandler): decorated handler

    """
    func.__require_login__ = True  # noqa:WPS609
    return func


@web.middleware
async def check_login(
    request: web.Request,
    handler: _WebHandler,  # noqa:WPS110
) -> web.StreamResponse:
    """
    Check request for session.

    Args:
        request (web.Request): request to process
        handler (_WebHandler): handler to process

    Returns:
        processed data

    """
    is_login_required = getattr(handler, '__require_login__', False)
    if is_login_required:
        await get_current_user_id(request)
    return await handler(request)


@web.middleware
async def check_for_body(
    request: web.Request,
    handler: _WebHandler,  # noqa:WPS110
) -> web.StreamResponse:
    """
    Check request for body.

    Args:
        request (web.Request): request to process
        handler (_WebHandler): handler to process

    Returns:
        processed data, if success or error if no body

    """
    if not request.can_read_body and request.method == 'POST':
        return web.json_response({'error': 'request has no body'})
    return await handler(request)
