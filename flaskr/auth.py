import functools
import datetime
from flask import (
    Blueprint, request, redirect, url_for, flash, render_template, session, g
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flaskr.forms import RegistrationForm, LoginForm, InformationForm, PWInformationForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
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
            return redirect(url_for('auth.update'))

        flash(error)

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))    

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
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    if request.form:
        form = PWInformationForm(request.form)
        
        username = request.form['username']
        sex = request.form['sex']
        email = request.form['email']
        birthdate = datetime.datetime.strptime(request.form['birthdate'], "%Y-%m-%d")
        updated = datetime.datetime.now()

        if 'whether_password' in request.form:
            validate = form.validate()
            sql_script = "UPDATE user SET username=?, email=?, sex=?, birthdate=?, updated=?, password=? WHERE id=?"
            values = (username, email, sex, birthdate, updated, generate_password_hash(request.form['password']), g.user['id'])
        else:
            validate = InformationForm(request.form).validate()
            sql_script = "UPDATE user SET username=?, email=?, sex=?, birthdate=?, updated=? WHERE id=?"
            values = (username, email, sex, birthdate, updated, g.user['id'])

    else:
        form = PWInformationForm(data=g.user) 
    
    if request.method == 'POST' and validate: 
        db = get_db()
        
        db.execute(
            sql_script,
            values 
        )
        db.commit()
        return redirect(url_for('auth.update'))
    return render_template('auth/update.html', form=form)
