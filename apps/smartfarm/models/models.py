from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sensor(db.Model):
    __tablename__ = 'sensors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    

class Crop(db.Model):
    __tablename__ = 'crops'

    crop_id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    bed_id = db.Column(db.Integer, db.ForeignKey('beds.bed_id'), nullable=True)
    planted_at = db.Column(db.DateTime, default=datetime.now)
    planting_date = db.Column(db.Date)
    harvest_date = db.Column(db.Date)
    
    status = db.Column(db.Enum(
        'planted', 'nutritional', 'reproductive', 'harvestable', 'harvested', 'failed',
        name='crop_status_enum'
    ))

    pest_disease_status = db.Column(db.Text)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Crop {self.crop_name} ({self.status})>"
    
    def to_dict(self):
        return {
            'crop_id': self.crop_id,
            'crop_name': self.crop_name,
            'user_id': self.user_id,
            'bed_id': self.bed_id,
            'planted_at': self.planted_at.isoformat(),
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'status': self.status,
            'pest_disease_status': self.pest_disease_status,
            'notes': self.notes
        }

class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    
    data_id = db.Column('data_id', db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column('sensor_id', db.Integer, nullable=False)
    sensor_type = db.Column('sensor_type', db.String(50), nullable=False)
    sensor_value = db.Column('sensor_value', db.Float, nullable=False)
    bed_id = db.Column('bed_id', db.Integer, nullable=False)
    recorded_at = db.Column('recorded_at', db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'data_id': self.data_id,
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type,
            'sensor_value': self.sensor_value,
            'bed_id': 1, #bed_id 임시값
            'recorded_at': self.recorded_at.isoformat()
        } 
    
class Device(db.Model):
    __tablename__ = 'devices'
    
    device_id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.String(50), nullable=False)
    status_now = db.Column(db.String(50), default='off')
    bed_id = db.Column(db.Integer, nullable=False)
    installed_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'status_now': self.status_now,
            'bed_id': self.bed_id,
            'installed_at': self.installed_at.isoformat()
        }
    
class HarvestLog(db.Model):
    __tablename__ = 'harvest_logs'

    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.crop_id'), nullable=False)  # ← 이 줄 추가
    harvested_at = db.Column(db.Date, nullable=False)
    weight_grams = db.Column(db.Float, nullable=False)
    bed_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'crop_id': self.crop_id,
            'harvested_at': self.harvested_at.isoformat(),
            'weight_grams': self.weight_grams,
            'bed_id': self.bed_id,
            'created_at': self.created_at.isoformat()
        }

class DeviceSchedule(db.Model):
    __tablename__ = 'device_schedules'
    
    schedule_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id'), nullable=False)
    on_time = db.Column(db.DateTime, nullable=False)
    off_time = db.Column(db.DateTime, nullable=False)
    status_now = db.Column(db.String(50), default='off')
    set_at = db.Column(db.DateTime, default=datetime.now)
    is_recurring = db.Column(db.Boolean, default=False)
    executed_at = db.Column(db.DateTime)

    # Device와의 관계 추가
    device = db.relationship('Device', backref='schedules')

    def to_dict(self):
        return {
            'schedule_id': self.schedule_id,
            'device_id': self.device_id,
            'device_type': self.device.device_type if self.device else None,  # device_type 추가
            'on_time': self.on_time.isoformat(),
            'off_time': self.off_time.isoformat(),
            'status_now': self.status_now,
            'set_at': self.set_at.isoformat(),
            'is_recurring': self.is_recurring,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

    __table_args__ = {'extend_existing': True}


    