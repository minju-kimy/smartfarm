from flask import Blueprint, request, render_template, redirect, url_for
from apps.smartfarm.models.models import db, HarvestLog, Crop, Device
from datetime import datetime
import pandas as pd
from flask import jsonify

harvest_bp = Blueprint('harvest', __name__, url_prefix='/smartfarm')

@harvest_bp.route('/harvest_mg', methods=['GET'])
def harvest_mg():
    crops = Crop.query.all()
    devices = Device.query.all()
    logs = HarvestLog.query.all()

    if not logs:
        return render_template('smartfarm/harvest_mg.html',
                               crops=crops,
                               devices=devices,
                               chart_all=[],
                               chart_by_crop={},
                               chart_multi={})

    # --- 데이터프레임 변환
    crop_map = {crop.crop_id: crop.crop_name for crop in crops}
    df = pd.DataFrame([
        (crop_map.get(l.crop_id), l.harvested_at, l.weight_grams)
        for l in logs
    ], columns=['crop_name', 'date', 'weight'])

    df['date'] = pd.to_datetime(df['date']).dt.strftime('%m.%d')

    df_total = df.groupby('date')['weight'].sum().reset_index()
    chart_all = df_total.to_dict(orient='records')

    chart_by_crop = {}
    for crop in df['crop_name'].unique():
        df_crop = df[df['crop_name'] == crop]
        df_crop_grouped = df_crop.groupby('date')['weight'].sum().reset_index()
        chart_by_crop[crop] = df_crop_grouped.to_dict(orient='records')

    df_multi = df.groupby(['date', 'crop_name'])['weight'].sum().unstack(fill_value=0).reset_index()
    chart_multi = {
        'labels': df_multi['date'].tolist(),
        'datasets': [
            {
                'label': crop,
                'data': df_multi[crop].tolist()
            }
            for crop in df_multi.columns if crop != 'date'
        ]
    }

    

    return render_template('smartfarm/harvest_mg.html',
                           crops=crops,
                           devices=devices,
                           chart_all=chart_all,
                           chart_by_crop=chart_by_crop,
                           chart_multi=chart_multi)


@harvest_bp.route('/harvest_mg/add', methods=['POST'])
def add_harvest():
    try:
        data = request.get_json()
        crop_name = data['crop_name']
        harvested_at = datetime.strptime(data['harvested_at'], '%Y-%m-%d')
        weight_grams = float(data['weight_grams'])

        new_log = HarvestLog(
            crop_name=crop_name,
            harvested_at=harvested_at,
            weight_grams=weight_grams
        )
        db.session.add(new_log)
        db.session.commit()

        return jsonify({'message': '수확 기록이 저장되었습니다.'})
    finally:
        db.session.remove()