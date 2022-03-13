import socketio
from socketio.exceptions import ConnectionRefusedError
from middleware import require_login
from aiohttp import web
from middleware import require_login
from aiohttp_session import get_session
from aiohttp_security import authorized_userid


sio = socketio.AsyncServer(async_mode='aiohttp')

NAMESPACE_INBOX = '/ws'


class WSInboxNamespace(socketio.AsyncNamespace):

    async def on_connect(self, sid, environ):
        """
        TODO: Now app doesnt care about many sessions for 1 user.
        TODO: IF there is new session than just update sid

        """
        aiohttp_request = environ.get('aiohttp.request')
        user = await authorized_userid(aiohttp_request)
        aiohttp_request.app['socketio_session'].update({user.username: sid})  # TODO what to do with many sessions
        if user:
            await sio.save_session(
                sid,
                {'username': user.username},
                namespace=NAMESPACE_INBOX,
            )
        #raise ConnectionRefusedError

    async def on_disconnect(self, sid):
        session = await sio.get_session(sid, namespace=NAMESPACE_INBOX)
        session.pop('username')
        print('SIO disconnected')

    async def on_message(self, sid, data):
        print('MSG', data)
        print('sid', sid)
        session = await sio.get_session(sid, namespace=NAMESPACE_INBOX)
        if session.get('username'):
            print(session['username'])
            await self.emit('message', {'new': 123})


sio.register_namespace(WSInboxNamespace('/ws'))


@require_login
async def socket_test(request: web.Request):
    await sio.handle_request(request)


async def close_sio_session(request: web.Request):
    user = await authorized_userid(request)
    sid = request.app['socketio_session'][user.username]
    session = await sio.get_session(
        sid=sid,
        namespace=NAMESPACE_INBOX,
    )
    session.pop('username')
    await sio.disconnect(
        sid=sid,
        namespace=NAMESPACE_INBOX,
    )

