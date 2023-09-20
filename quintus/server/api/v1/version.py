from flask import Blueprint
from .data import data
from .user import user

v1 = Blueprint("v1", __name__, url_prefix="/v1")
v1.register_blueprint(data)
v1.register_blueprint(user)
