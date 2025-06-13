from apps.smartfarm.routes.device_routes import device_bp
from apps.smartfarm.routes.sensor_routes import sensor_bp
from apps.smartfarm.routes.schedule_routes import schedule_bp
from apps.smartfarm.routes.chart_routes import chart_bp
from apps.smartfarm.routes.harvest_routes import harvest_bp

from apps.smartfarm.services.scheduler import scheduler, check_device_schedules
from apps.smartfarm.services.mqtt_service import MQTTService
from apps.extensions import socketio


def init_smartfarm(app):
    # Blueprint 등록
    app.register_blueprint(device_bp)
    app.register_blueprint(sensor_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(chart_bp)
    app.register_blueprint(harvest_bp)

    # 스케줄러 등록
    scheduler.init_app(app)
    if not scheduler.get_job('check_device_schedules'):
        scheduler.add_job(
            id='check_device_schedules',
            func=lambda: check_device_schedules(app),
            trigger='interval',
            seconds=30
        )
    if not scheduler.running:
        scheduler.start()
    app.apscheduler = scheduler

    # MQTT 서비스 시작
    with app.app_context():
        mqtt_service = MQTTService(app, socketio)
        mqtt_service.connect()
