import functools
from flask import (
    Blueprint, request, redirect, url_for, flash, render_template
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flaskr.forms import RegistrationForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']
        mobile_number = request.form['mobile_number']
        request_ip = request.remote_addr

        db = get_db()
        error = None

        if db.execute(
            'SELECT id FROM user WHERE username=? OR mobile_number=?',
            (username, mobile_number)
        ).fetchone() is not None:
            error = 'Username or mobile num is already registered'

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, mobile_number, request_ip)'
                ' VALUES (?, ?, ?, ?)',
                (username, generate_password_hash(password), mobile_number, request_ip)
            )
            db.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html', form=form)
