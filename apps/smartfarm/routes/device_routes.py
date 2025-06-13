from flask import Blueprint, jsonify, request, current_app, render_template
from flask_socketio import emit
from apps.config import Config
from apps.smartfarm.models.models import db, Device
from apps.smartfarm.services.mqtt_service import MQTTService  
import uuid
from datetime import datetime, timedelta
from flask import session
from functools import wraps

device_bp = Blueprint('device', __name__, url_prefix='/smartfarm')

def deny_if_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') == 'user':
            return jsonify({'error': '권한이 없습니다.'}), 403
        return f(*args, **kwargs)
    return decorated

@device_bp.route('/dashboard')
def smartfarm_dashboard():
    return render_template('smartfarm/dashboard.html') 

def auto_stop_motor(app, device_type, topic):
    with app.app_context():
        print(f"[Auto-Stop] Triggered for {device_type}")
        mqtt_service = MQTTService(current_app, current_app.extensions["socketio"])
        if mqtt_service.client.is_connected():
            mqtt_service.publish(topic, 'stop')
            print(f"[Auto-Stop] Published 'stop' to topic '{topic}'")

        # DB 상태도 'stop'으로 업데이트
        target_device = Device.query.filter_by(device_type=device_type).first()
        if target_device:
            target_device.status_now = 'stop'
            db.session.commit()
    
    db.session.remove()

def schedule_motor_stop_job(app, device_type, topic, delay_seconds):
    job_id = f"auto_stop_{device_type}_{uuid.uuid4()}"
    run_time = datetime.now() + timedelta(seconds=delay_seconds)

    app.apscheduler.add_job(
        id=job_id,
        func=auto_stop_motor,
        args=[app, device_type, topic],
        trigger='date',
        run_date=run_time,
        replace_existing=False
    )
    print(f"[Scheduler] Scheduled stop for {device_type} in {delay_seconds} sec (job: {job_id})")


@device_bp.route('/toggle_device', methods=['POST'])
@deny_if_user
def handle_toggle_device():
    try:
        print("\n=== Device Toggle Request ===")
        data = request.get_json()      
        device = data.get('device')      # 예: 'fan', 'led', 'motor1', 'motor2'
        state = data.get('state')        # 예: true / false 또는 'left', 'stop', 'right'

        print(f"Received request - Device: {device}, State: {state}")

        if not device:
            return jsonify({'error': 'Missing or empty device parameter'}), 400
        if state is None:
            return jsonify({'error': 'Missing state parameter'}), 400

        if device in Config.TOPICS:
            topic = Config.TOPICS[device]
            mqtt_service = MQTTService(current_app, current_app.extensions["socketio"])

            if mqtt_service.client.is_connected():
                # 모터인 경우: left/right/stop 처리 + 자동 stop 예약
                if device in ['motor1', 'motor2']:
                    if state not in ['left', 'right', 'stop']:
                        return jsonify({'error': 'Invalid state for motor'}), 400
                    state_str = state
                    mqtt_service.publish(topic, state_str)
                    print(f"[MQTT] Published '{state_str}' to topic '{topic}'")

                    # DB 상태 저장
                    target_device = Device.query.filter_by(device_type=device).first()
                    if target_device:
                        target_device.status_now = state_str
                        db.session.commit()

                    # 자동 stop 예약 분기
                    delay_map = {
                        ('motor1', 'right'): 11,
                        ('motor1', 'left'): 11.5,
                        ('motor2', 'left'): 11,
                        ('motor2', 'right'): 12
                    }
                    delay_seconds = delay_map.get((device, state))
                    if delay_seconds:
                        schedule_motor_stop_job(current_app._get_current_object(),device, topic, delay_seconds)

                else:
                    # 일반 장치 처리: true/false
                    state_str = 'true' if str(state).lower() in ['true', 'on', '1'] else 'false'
                    mqtt_service.publish(topic, state_str)
                    print(f"[MQTT] Published '{state_str}' to topic '{topic}'")

                    # DB 상태 저장
                    target_device = Device.query.filter_by(device_type=device).first()
                    if target_device:
                        target_device.status_now = 'on' if state_str == 'true' else 'off'
                        db.session.commit()

                return jsonify({'success': True, 'device': device, 'state': state})
            else:
                return jsonify({'error': 'MQTT client not connected'}), 500
        else:
            return jsonify({'error': 'Invalid device'}), 400
        

    except Exception as e:
        print(f"Error in handle_toggle_device: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.session.remove()