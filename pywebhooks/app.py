import logging
from multiprocessing import Process

from flask import Flask
from flask import abort, request, jsonify, g, url_for
from flask.ext.httpauth import HTTPBasicAuth
#from flask.ext.sqlalchemy import SQLAlchemy

from passlib.apps import custom_app_context as pwd_context

from pywebhooks.models import user
from pywebhooks.models.user import db
from pywebhooks import CONFIG, CELERY
from pywebhooks.tasks import fetch


_LOG = logging.getLogger(__name__)


def create_app():
    _LOG.info('PyWebHooks Server Starting')
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        CONFIG.sqlalchemy.database_uri
    app.config['SECRET_KEY'] = CONFIG.sqlalchemy.secret_key
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] =\
        CONFIG.sqlalchemy.commit_on_teardown

    db.init_app(app)

    celery_proc = Process(target=CELERY.worker_main, args=[['', '--beat']])
    celery_proc.start()
    _LOG.info('Celery started with PID: {}'.format(celery_proc.pid))

    return app


auth = HTTPBasicAuth()
flask_app = create_app()


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@flask_app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    if username is None or password is None or email is None:
        abort(400) # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400) # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user, email)
    db.session.commit()
    return jsonify({'username': user.username}), 201,\
        {'Location': url_for('get_user', id=user.id, _external=True)}


@flask_app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@flask_app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@flask_app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@flask_app.route('/test')
def test():
    fetch.request_version.apply_async(kwargs={'msg': 'hello world'})
    return 'Test initiated'

@flask_app.route('/')
def get_version():
    return jsonify({'v1': 'current'})