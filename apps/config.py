# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')

    # MySQL database URI with pymysql
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
        os.getenv('DB_USERNAME', 'minju'),
        os.getenv('DB_PASS', '132468'),
        os.getenv('DB_HOST', 'localhost'),
        os.getenv('DB_PORT', 3306),
        os.getenv('DB_NAME', 'smartfarm')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 50,
        "max_overflow": 30,
        "pool_timeout": 10,
        "pool_recycle": 120
    }


    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')    
    
    SOCIAL_AUTH_GITHUB  = False

    GITHUB_ID      = os.getenv('GITHUB_ID')
    GITHUB_SECRET  = os.getenv('GITHUB_SECRET')

    # Enable/Disable Github Social Login    
    if GITHUB_ID and GITHUB_SECRET:
         SOCIAL_AUTH_GITHUB  = True

    # 스케쥴 자동시작 제거
    SCHEDULER_API_ENABLED = True  # 필요에 따라 유지
    SCHEDULER_AUTOSTART = False   # 
    
    # MQTT 설정
    MQTT_BROKER = '14.32.231.191'
    MQTT_PORT = 1883
    MQTT_USERNAME = None  # 필요시 설정
    MQTT_PASSWORD = None  # 필요시 설정
    
    # MQTT 토픽 정의
    TOPICS = {
        'fan': 'smartfarm/fan/control',
        'led': 'smartfarm/led/control',
        'pump': 'smartfarm/pump/control',
        'co2': 'smartfarm/co2/control',
        'motor1': 'smartfarm/motor1/control',
        'motor2': 'smartfarm/motor2/control',
        'ec': 'smartfarm/ec_sensor/control',
        'ph': 'smartfarm/ph_sensor/control',
        'water_solenoid': 'smartfarm/water_solenoid/control',
        'nutrient_pump': 'smartfarm/nutrient_pump/control',
        'sensors_data': 'smartfarm/sensors/data',  # 통합 센서 데이터 토픽
        'ec_sensor_data': 'smartfarm/ec_sensor/data',  # EC 센서 데이터 토픽
        'ph_sensor_data': 'smartfarm/ph_sensor/data'   # PH 센서 데이터 토픽
    } 

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
