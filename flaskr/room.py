"""Chat room
"""
import os
import re
import hashlib
import datetime
import json
from flask import (
    Blueprint, render_template, request, g
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db, get_redis

bp = Blueprint('room', __name__)

@bp.route('/', methods=['GET', 'POST', 'DELETE'])
@login_required
def index():
    """Room page
    """
    redis = get_redis()
    sorted_set_name = "chat_room_{}"
    hash_name = "chat_room_{}_{}"
    
    if 'id' in request.form and re.match(r"^\d+$", request.form['id']) is not None:
        id = int(request.form['id'])
    if 'room_id' in request.form and re.match(r"^\w+$", request.form['room_id']) is not None:
        room_id = request.form['room_id']
          
    if request.method == 'POST':
        user_room_names = redis.zrevrange(sorted_set_name.format(g.user['id']), 0, -1)
        friend_room_names = redis.zrevrange(sorted_set_name.format(id), 0, -1)
        u_f_intersection = set(user_room_names).intersection(set(friend_room_names))

        room_name = None
        for name in u_f_intersection:
            if redis.hlen(name) == 2:
                room_name = name
                break
        created = datetime.datetime.now().timestamp()
        if room_name is None:
            dk = bytes(hash_name.format(g.user['id'], created), encoding='utf-8')
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
        
        redis.zadd(sorted_set_name.format(g.user['id']), {room_name: created})
        redis.zadd(sorted_set_name.format(id), {room_name: created}) 
    elif request.method == 'DELETE':
        redis.hdel(room_id, g.user['id'])
        redis.zrem(sorted_set_name.format(g.user['id']), room_id)
        if redis.hlen(room_id) <=1: redis.delete(room_id)

    user_room_names = redis.zrevrange(sorted_set_name.format(g.user['id']), 0, -1)
    user_rooms = []
    for user_room_name in user_room_names:
        values = redis.hgetall(user_room_name).values()
        values = list(map(lambda x: json.loads(x), values))
        user_rooms.append({"room_id": user_room_name, "users": values})
    return render_template('room/index.html', user_rooms=user_rooms)
