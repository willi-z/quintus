from flask import Blueprint, render_template, redirect  # noqa

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/data/all", methods=["GET"])
def dump_all():
    pass


@api.route("/data/single/<document>/<id>", methods=["GET"])
def request_entry(document: str, id: str):
    pass


@api.route("/data/single/<document>/<id>", methods=["UPDATE"])
def update_entry(document: str, id: str):
    pass
