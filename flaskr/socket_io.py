"""socket
"""
import functools
from flask import session
from flask_socketio import SocketIO, join_room, leave_room, disconnect, Namespace

from flaskr.db import get_db

socketio = SocketIO()

def authenticated_only(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        global user
        user_id = session.get('user_id')
        if user_id is None:
            user = None
            disconnect()
        else:
            user = get_db().execute(
                'SELECT * FROM user WHERE id=?',
                (user_id,)
            ).fetchone()
            return view(*args, **kwargs)
    return wrapped

class Notice(Namespace):
    """Notice container application and chat
    """
    @authenticated_only
    def on_join(self):
        """Join single notice room
        """
        join_room(f"notice_application_{user['id']}")
        return f"{user['username']} has entered the room"

socketio.on_namespace(Notice('/notice'))
