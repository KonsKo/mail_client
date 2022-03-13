"""Auth policy."""
import logging

import jwt
from aiohttp import web
from aiohttp.multipart import CIMultiDictProxy
from passlib.hash import pbkdf2_sha256
from service.user_service import UserService

logger = logging.getLogger(__name__)

JWT_SECRET_KEY = 'access_super_key'
JWT_ALGORITHM = 'HS256'


async def create_credentials(
    service: UserService,
    username: str,
    password: str,
) -> dict:
    """
    Create user credentials.

    Args:
        service (UserService): user-related service
        username (str): username
        password (str): password

    Returns:
        result (dict): result of creating

    """
    pass_hash = pbkdf2_sha256.hash(
        password,
    )
    return await service.create(
        request_body={
            'payload': {
                'username': username,
                'password_hash': pass_hash,
            },
        },
    )


def get_token_data(headers: CIMultiDictProxy) -> dict:
    """
    Decode and check JWT.

    Args:
        headers (CIMultiDictProxy): aiohttp request headers

    Returns:
        token (dict): decoded token

    Raises:
        HTTPUnauthorized: if error decoding JWT

    """
    auth_header = headers.get('Authorization')
    token = auth_header.replace('Bearer ', '')
    try:
        return jwt.decode(
            token,
            key=JWT_SECRET_KEY,
            algorithms=JWT_ALGORITHM,
        )
    except Exception as exception:
        logger.exception(
            'Authorization token decoding was failed. {0}'.format(
                exception,
            ),
        )
        raise web.HTTPUnauthorized()


async def get_current_user_id(request: web.Request) -> int:
    """
    Get user id from JWT.

    Args:
        request (web.Request): aiohttp request

    Returns:
        user_id (int): current user id

    Raises:
        HTTPUnauthorized: if JWT has no user data

    """
    decoded = get_token_data(headers=request.headers)
    user_id = decoded.get('user_id')
    if not user_id:
        raise web.HTTPUnauthorized()
    return user_id
