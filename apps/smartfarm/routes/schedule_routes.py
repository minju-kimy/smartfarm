from flask import Blueprint, request, jsonify, render_template
from apps.smartfarm.models.models import db, DeviceSchedule, Device
from datetime import datetime

schedule_bp = Blueprint('schedule', __name__, url_prefix='/smartfarm')

@schedule_bp.route('/schedules', methods=['GET'])
def list_schedules():
    schedules = DeviceSchedule.query.all()
    data = []
    for s in schedules:
        data.append({
            'schedule_id': s.schedule_id,
            'device_id': s.device_id,
            'device_type': s.device.device_type if s.device else None,
            'on_time': s.on_time.strftime('%Y-%m-%d %H:%M:%S'),
            'off_time': s.off_time.strftime('%Y-%m-%d %H:%M:%S') if s.off_time else None,
            'status_now': s.status_now,
            'set_at': s.set_at.strftime('%Y-%m-%d %H:%M:%S') if s.set_at else None,
            'executed_at': s.executed_at.strftime('%Y-%m-%d %H:%M:%S') if s.executed_at else None
        })
    return jsonify(data)

@schedule_bp.route('/schedules/list', methods=['GET'])
def get_schedule_list():
    schedules = DeviceSchedule.query.all()
    return jsonify([s.to_dict() for s in schedules])


@schedule_bp.route('/schedules/add', methods=['POST'])
def add_schedule():
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        on_time = datetime.strptime(data.get('on_time'), '%Y-%m-%d %H:%M:%S')
        off_time = datetime.strptime(data.get('off_time'), '%Y-%m-%d %H:%M:%S') if data.get('off_time') else None
        status_now = data.get('status_now', 'on')
        is_recurring = data.get('is_recurring', False)
        
        schedule = DeviceSchedule(
            device_id=device_id,
            on_time=on_time,
            off_time=off_time,
            status_now=status_now,
            set_at=datetime.now(),
            is_recurring=is_recurring
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify({'message': 'Schedule added successfully'})
    finally:
        db.session.remove()

@schedule_bp.route('/schedules/delete/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        schedule = DeviceSchedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({'message': 'Schedule deleted'})
    finally:
        db.session.remove()


@schedule_bp.route('/schedule_ui', methods=['GET'])
def schedule_ui():
    devices = Device.query.all()
    return render_template('smartfarm/schedule.html', devices=devices)