# -*- encoding: utf-8 -*-

import os
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit

from apps.config import config_dict
from apps import create_app, db
from apps.extensions import socketio  # SocketIO 추가

# 실행 모드 결정 (환경변수 DEBUG 기본값: False)
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
CONFIG_MODE = 'Debug' if DEBUG else 'Production'

# Flask 앱 생성
try:
    app_config = config_dict[CONFIG_MODE]
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production]')

app = create_app(app_config)
Migrate(app, db)

# Minify는 프로덕션에서만 활성화
if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

# 로그 출력 (DEBUG 모드에만)
if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT = ' + app_config.ASSETS_ROOT)

# SocketIO 실행
if __name__ == "__main__":
    # 개발용 포트는 5001, 필요시 수정 가능
    socketio.run(app, host='0.0.0.0', port=5001, debug=DEBUG)
