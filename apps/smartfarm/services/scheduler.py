from datetime import datetime, timedelta
from flask_apscheduler import APScheduler
from apps.smartfarm.models.models import db, DeviceSchedule, Device
from apps.config import Config
from apps.smartfarm.services.mqtt_service import MQTTService
from flask import current_app

scheduler = APScheduler()

def check_device_schedules(app):
    with app.app_context():
        try:
            now = datetime.now()
            print(f"\n[Scheduler] Checking schedules at {now.strftime('%Y-%m-%d %H:%M:%S')}")

            # === ON 스케줄 처리 ===
            on_schedules = DeviceSchedule.query.filter(
                DeviceSchedule.on_time <= now
            ).all()
            print(f"[Scheduler] Found {len(on_schedules)} ON schedules to process")

            for schedule in on_schedules:
                device = Device.query.get(schedule.device_id)
                if not device:
                    continue

                if not schedule.is_recurring and schedule.executed_at:
                    continue

                if device.status_now == 'on':
                    continue

                device_type = device.device_type.lower()
                topic = Config.TOPICS.get(device_type)
                if not topic:
                    continue

                mqtt_service = MQTTService(current_app, current_app.extensions["socketio"])
                if mqtt_service.client.is_connected():
                    mqtt_service.publish(topic, 'true')
                    device.status_now = 'on'
                    schedule.status_now = 'on'

                    if not schedule.is_recurring:
                        schedule.executed_at = now

                    db.session.commit()

            # === OFF 스케줄 처리 ===
            off_schedules = DeviceSchedule.query.filter(
                DeviceSchedule.off_time <= now
            ).all()
            print(f"[Scheduler] Found {len(off_schedules)} OFF schedules to process")

            for schedule in off_schedules:
                device = Device.query.get(schedule.device_id)
                if not device:
                    continue

                if not schedule.is_recurring and schedule.executed_at:
                    continue

                if device.status_now == 'off':
                    continue

                device_type = device.device_type.lower()
                topic = Config.TOPICS.get(device_type)
                if not topic:
                    continue

                mqtt_service = MQTTService(current_app, current_app.extensions["socketio"])
                if mqtt_service.client.is_connected():
                    mqtt_service.publish(topic, 'false')
                    device.status_now = 'off'
                    schedule.status_now = 'off'

                    if schedule.is_recurring:
                        schedule.on_time += timedelta(days=1)
                        schedule.off_time += timedelta(days=1)
                    else:
                        schedule.executed_at = now

                    db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"[Scheduler Error] {e}")

        finally:
            db.session.remove()
