"""Friend
search,add,delet,list friends
"""
import re
import datetime
from flask import (
    Blueprint, render_template, request, g, redirect, url_for, flash, make_response
)
from flaskr.auth import login_required
from flaskr.db import get_db, get_redis
from werkzeug.exceptions import abort

bp = Blueprint('friend', __name__, url_prefix='/friend')

@bp.route('/', methods=['GET','DELETE'])
@login_required
def index():
    db = get_db()
    if 'id' in request.form:
        id = int(request.form['id'])
        assert type(id) == int
    
    if request.method == 'DELETE':
        
        db.execute(
            'DELETE FROM friend WHERE sorted_key=? or sorted_key=?',
            (f"{g.user['id']}_{id}", f"{id}_{g.user['id']}")
        )
        db.commit()
        return make_response({'msg': 'success'}) 

    friends = db.execute(
        'SELECT friend_id, username, sex FROM friend f LEFT'
        ' JOIN user u ON friend_id = u.id'
        ' WHERE user_id=?'
        ' UNION'
        ' SELECT user_id as friend_id, username, sex FROM friend f LEFT'
        ' JOIN user u ON user_id = u.id'
        ' WHERE friend_id=?'
        ' ORDER BY username ASC',
        (g.user['id'], g.user['id'])
    ).fetchall()
    return render_template('friend/index.html', friends=friends)

def query_string_to_dict(query_string:str) -> dict:
    """query string transale to dictionary

    Args:
        query_string: query string form
    Return:
        dictionary from query string
    """
    cells = query_string.split('&')
    result = {}
    for cell in cells:
        cell = cell.split('=')
        if len(cell) == 1:
            raise TypeError("query_string`s format isn`t correct")
        result[cell[0]] = cell[1]

    return result

@bp.route('/search')
@login_required
def search():
    """Search user
    select users from sql table user where username or email is query
    Args:
        query: from request query_string
    Returns:
        friend/users.html with users
    """
    query_string = str(request.query_string, encoding='utf-8')
    if 'query' not in query_string:
        abort(401)

    query_dict = query_string_to_dict(query_string)
    query = query_dict['query']
    
    sql_script = "SELECT id, username, sex, birthdate FROM user \
        WHERE {} LIKE '%"+query+"%' AND id<>"+str(g.user['id'])+" \
        ORDER BY username ASC LIMIT 20"
    
    if re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', query):
        sql_script = sql_script.format('email')
    elif re.match(r'^\w{2,20}$', query):
        sql_script = sql_script.format('username')
    else:
        abort(401)
    
    users = get_db().execute(
        sql_script
    ).fetchall()
    
    return render_template('friend/search.html', users=users)

@bp.route('/<int:id>/send', methods=['GET', 'POST'])
@login_required
def send(id):
    """Send aplication
    from search result send friend application

    Args:
        id: user id 
    Return: 
        redirect to friend index when send success
        friend send.html
    """
    db = get_db()
    
    if request.method == 'POST':
        redis = get_redis()
        sorted_set_name = f"application_{id}" 
        hash_name = f"application_{id}_{g.user['id']}"
        
        redis.zrem(sorted_set_name, g.user['id'])
        redis.delete(hash_name)
         
        auth = db.execute(
            'SELECT username FROM user WHERE id=?',
            (g.user['id'],)
        ).fetchone()
        created = datetime.datetime.now().replace(microsecond=0).timestamp()
        auth = {"applicant_id": g.user['id'], "username": auth['username'], 
                "created": created, "message": request.form['message']}
        redis.zadd(sorted_set_name, {g.user['id']: created})
        redis.hmset(hash_name, auth)
        return redirect(url_for('friend.index'))
    
    user = db.execute(
        'SELECT id, username FROM user WHERE id=?',
        (id,)
    ).fetchone()
    return render_template('friend/send.html', user=user)

@bp.route('/application', methods=['GET', 'POST', 'DELETE'])
@login_required
def application():
    """Application
    Show application list and add application to friend

    Args:
        id: from user id
    Returns:
        application html or redirect to friend index
    """
    redis = get_redis()
    sorted_set_name = f"application_{g.user['id']}" 
    hash_name = "application_"+str(g.user['id'])+"_{}"

    if 'id' in request.form:
        id = int(request.form['id'])
        assert type(id) == int
    
    if request.method == 'POST':
        db = get_db()
        db.execute(
            "INSERT INTO friend (user_id, friend_id, sorted_key)"
            " VALUES (?, ?, ?)",
            (g.user['id'], id, f"{g.user['id']}_{id}")
        )
        db.commit()
        redis.delete(hash_name.format(id))
        redis.zrem(sorted_set_name, id)
        return redirect(url_for('friend.index'))

    elif request.method == 'DELETE':

        redis.delete(hash_name.format(id))
        redis.zrem(sorted_set_name, id)
        return make_response({'msg': 'success'})

    applicant_ids = redis.zrevrange(sorted_set_name, 0, -1)
    applications = []
    for applicant_id in applicant_ids:
        application = redis.hgetall(hash_name.format(applicant_id))
        applications.append(application)

    return render_template('friend/application.html', applications=applications)
