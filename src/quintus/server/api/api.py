from flask import Blueprint, redirect  # noqa
import flask_login as fl
from .v1 import v1

api = Blueprint("api", __name__, url_prefix="/api")


@api.before_request
@fl.login_required
def restrict_api_to_users():
    print(f"api.py: {fl.current_user}")


api.register_blueprint(v1)
