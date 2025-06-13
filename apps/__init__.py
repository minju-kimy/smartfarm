from flask import Flask, redirect, url_for
from importlib import import_module
from apps.extensions import db, login_manager, socketio
from apps.smartfarm import init_smartfarm
from apps.smartfarm.sockets.socket_handlers import register_socket_handlers



def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    socketio.init_app(app)

    # 확장 초기화
    db.init_app(app)
    login_manager.init_app(app)

    # 소켓 핸들러 등록
    register_socket_handlers(socketio)
    
    #db 세션 종료
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # 블루프린트 등록
    for module_name in ('authentication', 'home', 'smartfarm'):
        module = import_module(f'apps.{module_name}.routes')
        app.register_blueprint(module.blueprint)


    # 루트 URL 리다이렉션
    @app.route('/')
    def index():
        return redirect(url_for('authentication.login'))

    # 스마트팜 서비스 초기화
    init_smartfarm(app)

    return app
