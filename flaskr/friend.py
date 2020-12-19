"""Friend
search,add,delet,list friends
"""
import re
import datetime
import functools
from flask import (
    Blueprint, render_template, request, g, redirect, url_for, flash, make_response
)
from flask.views import MethodView
from flaskr.auth import login_required
from flaskr.db import get_db, get_redis
from flaskr.notice import notice_application
from werkzeug.exceptions import abort

bp = Blueprint('friend', __name__, url_prefix='/friend')

class Index(MethodView):
    """Friend get delete
    """
    decorators = [login_required]
    
    def get(self):
        """Show firends of user list
        """
        friends = get_db().execute(
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
    def delete(self):
        """Delete a friend of user
        """
        db = get_db()
        if 'id' in request.form:
            id = int(request.form['id'])
            assert type(id) == int

        db.execute(
            'DELETE FROM friend WHERE sorted_key=? or sorted_key=?',
            (f"{g.user['id']}_{id}", f"{id}_{g.user['id']}")
        )
        db.commit()
        return make_response({'msg': 'success'})

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

class SearchApplicate(MethodView):
    """Search user
    select users from sql table user where username or email is query
    Args:
        query: from request query_string
    Returns:
        friend/users.html with users
    """
    decorators = [login_required]
    def get(self):
        """Method get
        """
        query_string = str(request.query_string, encoding='utf-8')
        if 'query' not in query_string:
            abort(400)

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
            abort(400)
        
        users = get_db().execute(
            sql_script
        ).fetchall()
        
        return render_template('friend/search_applicate.html', users=users)
    def post(self):
        """Send aplication
        from search result send friend application

        Args:
            id: user id 
        Return: 
            redirect to friend index when send success
            friend send.html
        """
        if 'id' in request.form:
            id = int(request.form['id'])
            assert type(id) == int
        
        redis = get_redis()
        sorted_set_name = f"application_{id}" 
        hash_name = f"application_{id}_{g.user['id']}"
        
        redis.zrem(sorted_set_name, g.user['id'])
        redis.delete(hash_name)
         
        auth = get_db().execute(
            'SELECT username FROM user WHERE id=?',
            (g.user['id'],)
        ).fetchone()
        created = datetime.datetime.now().replace(microsecond=0).timestamp()
        auth = {"applicant_id": g.user['id'], "username": auth['username'], 
                "created": created, "message": request.form['message']}
        redis.zadd(sorted_set_name, {g.user['id']: created})
        redis.hmset(hash_name, auth)
        
        notice_application(id, hash_name, {'username': auth['username'], 'message': auth['message']}) 
        return redirect(url_for('friend.index'))

def get_args(view):
    """Get gobal arg
    """
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        redis = get_redis()
        sorted_set_name = f"application_{g.user['id']}" 
        hash_name = "application_"+str(g.user['id'])+"_{}"
        if 'id' in request.form:
            id = int(request.form['id'])
            assert type(id) == int
            return view(redis, sorted_set_name, hash_name, id, *args, **kwargs)
        return view(redis, sorted_set_name, hash_name, *args, **kwargs)
    return wrapped_view

class Application(MethodView):
    """Application
    Show application list and add application to friend

    Args:
        id: from user id
        Returns:
        application html or redirect to friend index
    """
    decorators = [login_required, get_args]
    def get(self, redis, sorted_set_name, hash_name):
        """Method get
        """
        applicant_ids = redis.zrevrange(sorted_set_name, 0, -1)
        applications = []
        for applicant_id in applicant_ids:
            application = redis.hgetall(hash_name.format(applicant_id))
            applications.append(application)

        return render_template('friend/application.html', applications=applications)
    def post(self, redis, sorted_set_name, hash_name, id):
        """Method post
        """
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
    def delete(self, redis, sorted_set_name, hash_name, id):
        redis.delete(hash_name.format(id))
        redis.zrem(sorted_set_name, id)
        return make_response({'msg': 'success'}) 

bp.add_url_rule('/', 
    view_func=Index.as_view('index'), 
    methods=['GET', 'DELETE'])
bp.add_url_rule('/search_applicate', 
    view_func=SearchApplicate.as_view('search_applicate'), 
    methods=['GET', 'POST'])
bp.add_url_rule('/application', view_func=Application.as_view('application'),
    methods=['GET', 'POST', 'DELETE'])
