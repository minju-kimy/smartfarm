from flask import Blueprint, jsonify
from apps.smartfarm.models.models import db, SensorData
from datetime import datetime
from datetime import timezone

sensor_bp = Blueprint('sensor', __name__)

@sensor_bp.route('/sensor_data')
def get_sensor_data():
    data = SensorData.query.order_by(SensorData.recorded_at.desc()).limit(10).all()
    return jsonify({'data': [{
        'timestamp': d.recorded_at.isoformat(),
        'sensor_type': d.sensor_type,
        'value': d.sensor_value
    } for d in data]}) 