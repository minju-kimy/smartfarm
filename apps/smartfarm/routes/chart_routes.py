
from flask import Blueprint, jsonify, render_template
from apps.smartfarm.models.models import db, SensorData, Crop, HarvestLog
from sqlalchemy import desc, func
from datetime import datetime, timedelta

chart_bp = Blueprint('chart', __name__, url_prefix='/smartfarm')

@chart_bp.route('/chart/temperature_data')
def temperature_data():
    try:
        three_days_ago = datetime.now() - timedelta(days=3)
        results = db.session.query(
            func.date_format(SensorData.recorded_at, '%Y-%m-%d %H:00').label('hour'),
            func.avg(SensorData.sensor_value).label('avg_value')
        ).filter(
            SensorData.sensor_type == 'temperature',
            SensorData.recorded_at >= three_days_ago
        ).group_by('hour')\
         .order_by('hour')\
         .all()

        labels = [r[0] for r in results]
        values = [round(r[1], 2) for r in results]
        return jsonify({'labels': labels, 'values': values})
    finally:
        db.session.remove()


@chart_bp.route('/chart/humidity_data')
def humidity_data():
    try:
        three_days_ago = datetime.now() - timedelta(days=3)
        results = db.session.query(
            func.date_format(SensorData.recorded_at, '%Y-%m-%d %H:00').label('hour'),
            func.avg(SensorData.sensor_value).label('avg_value')
        ).filter(
            SensorData.sensor_type == 'humidity',
            SensorData.recorded_at >= three_days_ago
        ).group_by('hour')\
         .order_by('hour')\
         .all()

        labels = [r[0] for r in results]
        values = [round(r[1], 2) for r in results]
        return jsonify({'labels': labels, 'values': values})
    finally:
        db.session.remove()


@chart_bp.route('/chart/co2_data')
def co2_data():
    try:
        three_days_ago = datetime.now() - timedelta(days=3)
        results = db.session.query(
            func.date_format(SensorData.recorded_at, '%Y-%m-%d %H:00').label('hour'),
            func.avg(SensorData.sensor_value).label('avg_value')
        ).filter(
            SensorData.sensor_type == 'co2',
            SensorData.recorded_at >= three_days_ago
        ).group_by('hour')\
         .order_by('hour')\
         .all()

        labels = [r[0] for r in results]
        values = [round(r[1], 2) for r in results]
        return jsonify({'labels': labels, 'values': values})
    finally:
        db.session.remove()


@chart_bp.route('/chart/ec_data')
def ec_data():
    try:
        results = db.session.query(
            func.date(SensorData.recorded_at).label('date'),
            SensorData.sensor_value
        ).filter(
            SensorData.sensor_type == 'ec'
        ).order_by(
            func.date(SensorData.recorded_at)
        ).all()

        labels = [r.date.strftime('%m.%d') for r in results]
        values = [r.sensor_value for r in results]

        return jsonify({'labels': labels, 'values': values})
    finally:
        db.session.remove()


@chart_bp.route('/chart/ph_data')
def ph_data():
    try:
        three_days_ago = datetime.now() - timedelta(days=3)
        results = SensorData.query.filter(
            SensorData.sensor_type == 'ph',
            SensorData.recorded_at >= three_days_ago
        ).order_by(desc(SensorData.recorded_at)).limit(50).all()
        results = sorted(results, key=lambda x: x.recorded_at)
        labels = [r.recorded_at.strftime('%H:%M') for r in results]
        values = [r.sensor_value for r in results]
        return jsonify({'labels': labels, 'values': values})
    finally:
        db.session.remove()


@chart_bp.route('/chart/latest_sensor_values')
def latest_sensor_values():
    try:
        sensor_types = ['temperature', 'humidity', 'co2']
        latest_values = {}

        for sensor in sensor_types:
            record = SensorData.query.filter_by(sensor_type=sensor)\
                .order_by(desc(SensorData.recorded_at))\
                .first()

            latest_values[sensor] = round(record.sensor_value, 2) if record else None

        return jsonify(latest_values)
    finally:
        db.session.remove()

@chart_bp.route('/chart/cumulative_harvest')
def cumulative_harvest():
    try:
        # 전체 수확 데이터를 날짜별로 정렬해서 가져옴
        results = db.session.query(
            func.date(HarvestLog.harvested_at).label('date'),
            func.sum(HarvestLog.weight_grams).label('daily_sum')
        ).group_by('date')\
         .order_by('date')\
         .all()

        labels = []
        values = []
        cumulative_sum = 0

        for row in results:
            labels.append(row.date.strftime('%Y-%m-%d'))
            cumulative_sum += float(row.daily_sum)
            values.append(round(cumulative_sum, 2))

        return jsonify({'labels': labels, 'values': values})
    finally:
        db.session.remove()

