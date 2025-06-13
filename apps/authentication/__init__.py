# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Blueprint

blueprint = Blueprint('authentication', __name__, url_prefix='/auth')

from apps.authentication import routes
