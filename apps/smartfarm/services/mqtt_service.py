import paho.mqtt.client as mqtt
from apps.config import Config
from apps.smartfarm.services.data_ingestion_service import DataIngestionService
from flask_socketio import SocketIO
from flask import current_app
import uuid

mqtt_service_instance = None

class MQTTService:
    def __new__(cls, app=None, socketio=None):
        global mqtt_service_instance
        if mqtt_service_instance is None:
            cls._instance = super(MQTTService, cls).__new__(cls)
            # 고유한 클라이언트 ID 생성
            client_id = f"smartfarm_server_{uuid.uuid4().hex[:8]}"
            print(f"Creating MQTT client with ID: {client_id}")
            cls._instance.client = mqtt.Client(client_id=client_id, clean_session=True)
            cls._instance.app = app
            cls._instance.socketio = socketio
            cls._instance.data_ingestion_service = DataIngestionService(app, socketio)
            mqtt_service_instance = cls._instance
        return mqtt_service_instance

    def connect(self):
        print("\n=== MQTT Connection Initialization ===")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect
        
        if Config.MQTT_USERNAME and Config.MQTT_PASSWORD:
            print(f"Setting MQTT credentials for user: {Config.MQTT_USERNAME}")
            self.client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
        
        try:
            print(f"Connecting to MQTT broker at {Config.MQTT_BROKER}:{Config.MQTT_PORT}")
            # 연결 옵션 설정
            self.client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, keepalive=60)
            self.client.loop_start()
            print("MQTT client loop started")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("\n=== MQTT Connection Successful ===")
            print("Connected to MQTT Broker!")
            # 디바이스 제어 토픽 구독
            for topic in Config.TOPICS.values():
                client.subscribe(topic)
                print(f"Subscribed to topic: {topic}")
            
            # 센서 데이터 토픽 구독
            sensor_topics = [
                'smartfarm/sensors/data',
                'smartfarm/ec_sensor/data',
                'smartfarm/ph_sensor/data'
            ]
            for topic in sensor_topics:
                client.subscribe(topic)
                print(f"Subscribed to sensor topic: {topic}")
        else:
            print(f"\n=== MQTT Connection Failed ===")
            print(f"Failed to connect, return code {rc}")
            print("Connection flags:", flags)

    def on_disconnect(self, client, userdata, rc):
        print(f"\n=== MQTT Disconnected ===")
        print(f"Disconnected with result code: {rc}")
        if rc != 0:
            print("Unexpected disconnection. Attempting to reconnect...")
            self.connect()

    def on_publish(self, client, userdata, mid):
        print(f"\n=== MQTT Message Published ===")
        print(f"Message ID: {mid}")

    def on_message(self, client, userdata, msg):
        # print(f"\n=== New MQTT Message ===\nTopic: {msg.topic}\nPayload: {msg.payload}\n======================\n")

        # Flask 컨텍스트 내에서 메시지 처리
        with self.app.app_context():
            self.data_ingestion_service.process_sensor_data(msg.topic, msg.payload)

    def publish(self, topic, payload):
        try:
            print(f"\n=== Attempting to Publish MQTT Message ===")
            print(f"Topic: {topic}")
            print(f"Payload: {payload}")
            print(f"Client connected: {self.client.is_connected()}")
            
            if not self.client.is_connected():
                print("Client not connected, attempting to reconnect...")
                self.connect()
            
            result = self.client.publish(topic, payload, qos=1)
            print(f"Publish result: {result}")
            print(f"Message ID: {result.mid}")
            print(f"Return code: {result.rc}")
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print("Message published successfully")
            else:
                print(f"Failed to publish message. Error code: {result.rc}")
                
        except Exception as e:
            print(f"Error in publish: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise 