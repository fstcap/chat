"""Chat room
"""
import os
import re
import hashlib
import datetime
import json
from flask import (
    Blueprint, render_template, request, g, redirect, url_for
)
from flask.views import MethodView
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db, get_redis

bp = Blueprint('room', __name__)

class Index(MethodView):
    """Chat room
    """
    decorators = [login_required]
    sorted_set_name = "chat_room_{}"
    hash_name = "chat_room_{}_{}"
    def get(self):
        """Method get
        """
        redis = get_redis()
        
        user_room_names = redis.zrevrange(self.sorted_set_name.format(g.user['id']), 0, -1)
        user_rooms = []
        for user_room_name in user_room_names:
            values = redis.hgetall(user_room_name).values()
            values = list(map(lambda x: json.loads(x), values))
            user_rooms.append({"room_id": user_room_name, "users": values})
        return render_template('room/index.html', user_rooms=user_rooms)
    def post(self):
        """Mehtod post
        """
        redis = get_redis()
        if 'id' not in request.form or re.match(r"^\d+$", request.form['id']) is None:
            abort(400)
        id = int(request.form['id'])
        user_room_names = redis.zrevrange(self.sorted_set_name.format(g.user['id']), 0, -1)
        friend_room_names = redis.zrevrange(self.sorted_set_name.format(id), 0, -1)
        u_f_intersection = set(user_room_names).intersection(set(friend_room_names))

        room_name = None
        for name in u_f_intersection:
            if redis.hlen(name) == 2:
                room_name = name
                break
        created = datetime.datetime.now().timestamp()
        if room_name is None:
            dk = bytes(self.hash_name.format(g.user['id'], created), encoding='utf-8')
            dk = hashlib.pbkdf2_hmac('sha256', dk, os.urandom(16), 100000)
            room_name = dk.hex()
            
            db = get_db()
            user = db.execute(
                'SELECT username FROM user WHERE id=?',
                (g.user['id'],)
            ).fetchone()
            friend = db.execute(
                'SELECT username FROM user WHERE id=?',
                (id,)
            ).fetchone()

            members = {
                g.user['id']: json.dumps({'id': g.user['id'], 'username': user['username']}), 
                id: json.dumps({'id': id, 'username': friend['username']})}
            redis.hmset(room_name, members)
        
        redis.zadd(self.sorted_set_name.format(g.user['id']), {room_name: created})
        redis.zadd(self.sorted_set_name.format(id), {room_name: created}) 
        return redirect(location=url_for('room.index'))
    def delete(self):
        """Method delete
        """
        redis = get_redis()
        if 'room_id' not in request.form or re.match(r"^\w+$", request.form['room_id']) is None:
            abort(400)
        room_id = request.form['room_id']
        redis.hdel(room_id, g.user['id'])
        redis.zrem(self.sorted_set_name.format(g.user['id']), room_id)
        if redis.hlen(room_id) <=1: redis.delete(room_id)
        return redirect(url_for('room.index'))

bp.add_url_rule('/', view_func=Index.as_view('index'), methods=['GET', 'POST', 'DELETE'])
