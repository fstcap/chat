from flask import Blueprint, request, make_response, g
from flask.views import MethodView
from werkzeug.exceptions import abort

from flaskr.db import get_redis
from flaskr.auth import login_required
from flask_socketio import emit

bp = Blueprint('notice', __name__, url_prefix='/notice')

def notice_application(id, hash_name, json):
    """Notice application
    Args:
        id: table user id
        hash_name: application user hash name
        json: applicator name and message
    """
    redis = get_redis()
    notice_name = f"application_notice_{id}"
    redis.lpush(notice_name, hash_name)
    emit('application', json, 
        namespace='/notice',
        room=f"notice_application_{id}")

class Application(MethodView):
    """Application notice get delete
    """
    decorators = [login_required]
    notice_name = "application_notice_{}"
    def get(self):
        """Get application notice len
        
        Return:
            notice_len: number of application len
        """
        redis = get_redis()
        notice_len = redis.llen(self.notice_name.format(g.user['id']))
        return make_response({"notice_len": notice_len})
    def delete(self):
        """Delete notice one by one
        Return:
            status_code: 0 or 1
        """
        redis = get_redis()
        redis.delete(self.notice_name.format(g.user['id']))
        return make_response({"message": "success"})
bp.add_url_rule('/application', view_func=Application.as_view('application'),
    methods=['GET', 'DELETE'])
