from flask_socketio import emit
from apps.smartfarm.models.models import SensorData
from apps.extensions import db

def register_socket_handlers(socketio):

    @socketio.on('get_latest_sensor_data')
    def send_latest_sensor_data():
        try:
            latest = SensorData.query.order_by(SensorData.recorded_at.desc()).first()
            if latest:
                emit('sensor_update', {
                    'temperature': latest.sensor_value if latest.sensor_type == 'temperature' else None,
                    'humidity': latest.sensor_value if latest.sensor_type == 'humidity' else None,
                    'co2': latest.sensor_value if latest.sensor_type == 'co2' else None,
                    'ec': latest.sensor_value if latest.sensor_type == 'ec' else None,
                    'ph': latest.sensor_value if latest.sensor_type == 'ph' else None,
                })
        except Exception as e:
            print(f"[SocketIO Error] {e}")
        finally:
            db.session.remove()
