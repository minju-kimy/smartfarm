# apps/smartfarm/routes/__init__.py

from flask import Blueprint

from apps.smartfarm.routes.device_routes import device_bp
from apps.smartfarm.routes.sensor_routes import sensor_bp
from apps.smartfarm.routes.schedule_routes import schedule_bp
from apps.smartfarm.routes.chart_routes import chart_bp
from apps.smartfarm.routes.harvest_routes import harvest_bp
blueprint = Blueprint('smartfarm', __name__, url_prefix='/smartfarm')

blueprint.register_blueprint(device_bp, url_prefix='/api')
blueprint.register_blueprint(sensor_bp, url_prefix='/api')
blueprint.register_blueprint(schedule_bp)
blueprint.register_blueprint(chart_bp)
blueprint.register_blueprint(harvest_bp)
