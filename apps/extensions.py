# apps/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

socketio = SocketIO(manage_session=False, cors_allowed_origins="*")
db = SQLAlchemy()
login_manager = LoginManager()
scheduler = APScheduler()

