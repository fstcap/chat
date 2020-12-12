"""User register, login, loginout, update informations, login check
"""

import functools
import datetime
from flask import (
    Blueprint, request, redirect, url_for, flash, render_template, session, g
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flaskr.forms import RegistrationForm, LoginForm, InformationForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """ Register user

    
    """
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        request_ip = request.remote_addr

        db = get_db()
        error = None

        if db.execute(
            'SELECT id FROM user WHERE username=? OR email=?',
            (username, email)
        ).fetchone() is not None:
            error = 'Username or email num is already registered'

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, email, request_ip)'
                ' VALUES (?, ?, ?, ?)',
                (username, generate_password_hash(password), email, request_ip)
            )
            db.commit()
            return redirect(url_for('auth.login'))
        
        flash(error)
    
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username=?',
            (username,)
        ).fetchone()

        if user is None:
            error = '用户名不正确'
        elif not check_password_hash(user['password'], password):
            error = '密码不正确'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True
            return redirect(url_for('room.index'))

        flash(error)

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))    

@bp.before_app_request
def load_logged_in_user():
    user_id =session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def login_required(view):
    """Check login
    
    """
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view

@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    """Update user informations
    Show user html page with information whem method is get.
    Post form data and validate it, update user table in sqlite3 by form data when method is post

    Args:
        formdata in request.form, user in g.user
    
    Returns:
        A update html page with user user information when edit fail.
        Redirect to index when edit success.
    
    """
    if request.method == 'POST':
        check_password = True if 'check_password' in request.form else False
        form = InformationForm(formdata=request.form) 
    else:
        form = InformationForm(data=g.user)  
    
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        sex = request.form['sex']
        email = request.form['email']
        birthdate = datetime.datetime.strptime(request.form['birthdate'], "%Y-%m-%d")
        updated = datetime.datetime.now().replace(microsecond=0)

        db = get_db()
        error = None

        if db.execute(
            'SELECT id FROM user WHERE username=? AND id<>?',(username, g.user['id'])
        ).fetchone() is not None:
            error = '用户名已存在'
        elif db.execute(
            'SELECT id FROM user WHERE email=? AND id<>?',(email, g.user['id'])
        ).fetchone() is not None:
            error = '邮箱已存在'
        
        if error is None:
            
            if check_password:
                sql_script = "UPDATE user SET username=?, email=?, \
                        sex=?, birthdate=?, updated=?, password=? WHERE id=?"
                values = (username, email, sex, birthdate, updated, 
                        generate_password_hash(request.form['password']), g.user['id'])
            else:
                sql_script = "UPDATE user SET username=?, email=?, \
                        sex=?, birthdate=?, updated=? WHERE id=?"
                values = (username, email, sex, birthdate, updated, g.user['id'])

            db.execute(
                sql_script,
                values 
            )
            db.commit()
            return redirect(url_for('room.index'))
        flash(error)
    return render_template('auth/update.html', form=form)
