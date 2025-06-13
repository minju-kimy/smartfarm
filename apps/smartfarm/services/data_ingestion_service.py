import json
from datetime import datetime
from datetime import timezone
from apps.smartfarm.models.models import db, SensorData, Sensor
from flask_socketio import emit

class DataIngestionService:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.sensor_data = {
            'temperature': None,
            'humidity': None,
            'co2': None,
            'ec': None,
            'ph': None,
            'waterlevel': None
        }
        # 센서 ID 매핑 (실제 센서 ID로 변경 필요)
        """
        self.sensor_ids = {
            'temperature': 1,
            'humidity': 4,
            'co2': 5,
            'ec': 6,
            'ph': 7,
            'waterlevel': 8
        }"""

        # 센서 타입별 유효 범위 정의
        self.sensor_ranges = {
            'temperature': {'min': -10, 'max': 50},
            'humidity': {'min': 0, 'max': 150},
            'co2': {'min': 0, 'max': 7000},  # CO2 범위 설정
            'ec': {'min': 0, 'max': 10000},
            'ph': {'min': 0, 'max': 14},
            'waterlevel': {'min': 0, 'max': 100}
        }

        # # 센서 ID 매핑 test
        self.sensor_ids = {
            'temperature': 1,
            'humidity': 2,
            'co2': 3,
            'ec': 4,
            'ph': 5,
            'waterlevel': 6
        }

    def process_sensor_data(self, topic, payload):
        try:
            # 제어 토픽인 경우 센서 데이터 처리하지 않음
            if topic.endswith('/control'):
                return

            # 센서 데이터 토픽인 경우에만 JSON 파싱 시도
            if topic in ['smartfarm/sensors/data', 'smartfarm/ec_sensor/data', 'smartfarm/ph_sensor/data']:
                try:
                    data = json.loads(payload.decode('utf-8'))
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON payload: {payload}")
                    return
            else:
                return
            
            timestamp = datetime.now()
            sensor_data_list = []
            
            # 토픽별로 데이터 처리 및 저장
            if topic == 'smartfarm/sensors/data':
                # print("Processing integrated sensor data...")
                # 온도 데이터 저장
                if 'temperature' in data:
                    # print(f"Processing temperature data: {data['temperature']}")
                    sensor_data = SensorData(
                        sensor_id=self.sensor_ids['temperature'],
                        sensor_type='temperature',
                        sensor_value=data['temperature'],
                        bed_id=1,  # 기본 bed_id 설정
                        recorded_at=timestamp
                    )
                    sensor_data_list.append(sensor_data)
                    self.sensor_data['temperature'] = data['temperature']
                    # print("Temperature data added to list")

                # 습도 데이터 저장
                if 'humidity' in data:
                    # print(f"Processing humidity data: {data['humidity']}")
                    sensor_data = SensorData(
                        sensor_id=self.sensor_ids['humidity'],
                        sensor_type='humidity',
                        sensor_value=data['humidity'],
                        bed_id=1,  # 기본 bed_id 설정
                        recorded_at=timestamp
                    )
                    sensor_data_list.append(sensor_data)
                    self.sensor_data['humidity'] = data['humidity']
                    # print("Humidity data added to list")

                # CO2 데이터 저장
                if 'co2' in data:
                    # print(f"Processing CO2 data: {data['co2']}")
                    sensor_data = SensorData(
                        sensor_id=self.sensor_ids['co2'],
                        sensor_type='co2',
                        sensor_value=data['co2'],
                        bed_id=1,  # 기본 bed_id 설정
                        recorded_at=timestamp
                    )
                    sensor_data_list.append(sensor_data)
                    self.sensor_data['co2'] = data['co2']
                    # print("CO2 data added to list")

                # 수위 데이터 저장
                if 'waterlevel' in data:
                    # print(f"Processing water level data: {data['waterlevel']}")
                    sensor_data = SensorData(
                        sensor_id=self.sensor_ids['waterlevel'],
                        sensor_type='waterlevel',
                        sensor_value=data['waterlevel'],
                        bed_id=1,  # 기본 bed_id 설정
                        recorded_at=timestamp
                    )
                    sensor_data_list.append(sensor_data)
                    self.sensor_data['waterlevel'] = data['waterlevel']
                    # print("Water level data added to list")

            elif topic == 'smartfarm/ec_sensor/data':
                if 'ec' in data:
                    # print(f"Processing EC data: {data['ec']}")
                    sensor_data = SensorData(
                        sensor_id=self.sensor_ids['ec'],
                        sensor_type='ec',
                        sensor_value=data['ec'],
                        bed_id=1,  # 기본 bed_id 설정
                        recorded_at=timestamp
                    )
                    sensor_data_list.append(sensor_data)
                    self.sensor_data['ec'] = data['ec']
                    # print("EC data added to list")

            elif topic == 'smartfarm/ph_sensor/data':
                if 'ph' in data:
                    # print(f"Processing pH data: {data['ph']}")
                    sensor_data = SensorData(
                        sensor_id=self.sensor_ids['ph'],
                        sensor_type='ph',
                        sensor_value=data['ph'],
                        bed_id=1,  # 기본 bed_id 설정
                        recorded_at=timestamp
                    )
                    sensor_data_list.append(sensor_data)
                    self.sensor_data['ph'] = data['ph']
                    # print("pH data added to list")

            # 모든 데이터를 한 번에 저장
            if sensor_data_list:
                # print("Adding all sensor data to session...")
                for sensor_data in sensor_data_list:
                    db.session.add(sensor_data)
                
                # print("Committing changes to database...")
                db.session.commit()
                # print("Changes committed successfully")

            # Socket.IO로 실시간 데이터 전송
            # print("Emitting sensor update...")
            self.socketio.emit('sensor_update', self.sensor_data)
            # print("Sensor update emitted")
                
        except Exception as e:
            print(f"Error processing sensor data: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            db.session.rollback()

        finally:
            db.session.remove()

    def _process_integrated_sensor_data(self, data):
        for sensor_type, value in data.items():
            if sensor_type in self.sensor_types:
                try:
                    float_value = float(value)
                    if not (self.sensor_types[sensor_type]['min'] <= float_value <= self.sensor_types[sensor_type]['max']):
                        print(f"Invalid {sensor_type} value: {float_value}")
                        continue
                        
                    sensor = Sensor.query.filter_by(sensor_type=sensor_type).first()
                    if not sensor:
                        sensor = Sensor(sensor_type=sensor_type, sensor_model='default')
                        db.session.add(sensor)
                        db.session.commit()
                        
                    sensor_data = SensorData(
                        sensor_id=sensor.sensor_id,
                        sensor_type=sensor_type,
                        sensor_value=float_value,
                        recorded_at=datetime.now(timezone.utc)
                    )
                    db.session.add(sensor_data)
                    
                except (ValueError, TypeError) as e:
                    print(f"Error processing {sensor_type} data: {e}")
                    continue
                
        
        try:
            db.session.commit()
            self.socketio.emit('sensor_update', data)
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {e}")
        finally:
            db.session.remove()

    def _process_ph_sensor_data(self, payload):
        try:
            data = json.loads(payload.decode())
            ph_value = float(data.get('ph', 0))
            if 0 <= ph_value <= 14:
                self.socketio.emit('sensor_update', {'ph': ph_value})
            else:
                print(f"Invalid pH value: {ph_value}")
        except (ValueError, TypeError) as e:
            print(f"Error processing pH data: {e}")

    def _process_ec_sensor_data(self, payload):
        try:
            data = json.loads(payload.decode())
            ec_value = float(data.get('ec', 0))
            if 0 <= ec_value <= 10000:
                self.socketio.emit('sensor_update', {'ec': ec_value})
            else:
                print(f"Invalid EC value: {ec_value}")
        except (ValueError, TypeError) as e:
            print(f"Error processing EC data: {e}") 