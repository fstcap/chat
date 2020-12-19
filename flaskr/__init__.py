import os
from datetime import timedelta
from flask import Flask
from flask_socketio import SocketIO

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        PERMANENT_SESSION_LIFETIME=timedelta(days=31),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
     
    from . import db, auth, room, friend, notice
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(room.bp)
    app.add_url_rule('/', endpoint='index')
    app.register_blueprint(friend.bp)
    app.register_blueprint(notice.bp)

    from .socket_io import socketio
    socketio.init_app(app)

    return app
