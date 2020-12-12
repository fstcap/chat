import pytest
import datetime
from flask import g, session
from flaskr.db import get_db
from werkzeug.security import check_password_hash

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
            '/auth/register', data={'username': 'bruce', 'email': 'fstcap@qq.com', 'password': 'qwerty123', 'confirm': 'qwerty123'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM user WHERE username="bruce"'
        ).fetchone() is not None

@pytest.mark.parametrize(
    ('username', 'email', 'password', 'confirm', 'messages'), (
        ('', '', '', '', ('请输入正确用户名', '请输入正确邮箱', '请输入正确密码')),
        ('qwertyuiopqwertyuiopq', 'fstqq.com', 'qwertyui', 'qwe', ('请输入正确用户名', '请输入正确邮箱', '请输入正确密码', '密码不匹配')),
        ('<html>qeerete', 'fst@qq.mpv', '###qqqqqqqqq', '###qqqqqqqqq', ('请输入正确用户名')),
        ('test', 'fst@163.com', 'qwerty123', 'qwerty123', ('Username or email num is already registered')),
        ('test1', 'fstcap@qq.com', 'qwerty123', 'qwerty123', ('Username or email num is already registered'))
    )
)
def test_regiser_validate_input(client, username, email, password, confirm, messages):
    response = client.post(
        '/auth/register',
        data={'username': username, 'email': email, 'password': password, 'confirm': confirm})
    
    for message in messages:
        assert bytes(message, encoding='utf-8') in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/auth/update'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(
    ('username', 'password', 'message'), (
        ('bruce1', 'qwerty123', '用户名不正确'),
        ('test', 'qwerty1234', '密码不正确')
    )
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    print(f"\033[0;35m{str(response.data, encoding='utf-8')}\033[0m")
    assert bytes(message, encoding='utf-8') in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

def test_login_required(client):
    response = client.get('/auth/update')
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_update(client, auth, app):
    auth.login()
    assert client.get('/auth/update').status_code == 200
    formdata = {'username': 'bruce',
        'sex': 'female',
        'email': 'brucefst@163.com',
        'birthdate': '1992-01-17',
        'check_password': 'y',
        'password': 'qwerty123',
        'confirm': 'qwerty123'}
    
    client.post('/auth/update',
        data=formdata)

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM user WHERE id=1').fetchone()
        post = dict(post)
    
    assert post['username'] == formdata['username']
    assert post['sex'] == formdata['sex']
    assert post['email'] == formdata['email']
    assert datetime.datetime.strftime(post['birthdate'], "%Y-%m-%d") == formdata['birthdate']
    assert check_password_hash(post['password'], formdata['password'])

@pytest.mark.parametrize(
    ('username', 'sex', 'email', 'birthdate', 'check_password', 'password', 'confirm', 'messages'),
    (
        ('', '', '', '', 'y', '', '', 
            ('请输入正确用户名', 'Input error', '请输入正确邮箱', '请输入正确时间格式', '请输入正确密码')),
        ('fst_32', 'female', 'qwer@163.com', '1992-01-17', 'y', 'qwertyuiop', 'qwertyu', 
            ('请输入正确密码', '密码不匹配')),
        ('fst_32', 'female', 'qwer@163.com', '1992-01-00', '', '', '', 
            ('请输入正确时间格式'))
    )
)
def test_update_validate_input(client, auth, username, sex, email, birthdate, check_password, password, confirm, messages):
    auth.login()
    assert client.get('/auth/update').status_code == 200
    response = client.post('/auth/update', 
        data={'username': username,
            'sex': sex,
            'email': email,
            'birthdate': birthdate,
            'check_password': check_password,
            'password': password,
            'confirm': confirm})
    
    for message in messages:
        assert bytes(message, encoding='utf-8') in response.data
