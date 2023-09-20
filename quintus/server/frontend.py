import uuid
import base64
from flask import Blueprint, request, render_template, redirect, abort, session
from quintus.server.api import api
from quintus.server.helpers import login_user, get_user_db, get_data_db

frontend = Blueprint("frontend", __name__, url_prefix="/", template_folder="templates")


@frontend.route("/")
def home():
    return render_template("pages/home.html")


@frontend.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        unique = request.form.get("user")
        password = request.form.get("password")
        if unique is None or password is None:
            return abort(401)

        conn = get_user_db()
        with conn.cursor() as cur:
            token = login_user(cur, unique, password)

        if token is None:
            return abort(401)
        session["token"] = token
        return redirect("/")
    return render_template("pages/login.html")


@frontend.route("/logout")
def logout():
    pass


@frontend.route("/overview")
def overview():
    materials = []
    for entry in get_data_db().document.find(dict()):
        material = dict()
        material["id"] = entry["_id"]
        material["url"] = f"{api.url_prefix}/{material['id']}"
        materials.append(material)
    return render_template("pages/overview.html")


def generate_id():
    identifier = uuid.uuid1()
    only_upper = base64.b32encode(identifier.bytes).decode("utf-8")
    short = only_upper[:8]
    return short


@frontend.route("/entry/<materialID>")
def get_material(materialID):
    if materialID == "new":
        # create short!!! uuid
        uid = generate_id()
        # check if already exists if not generate again
        db = get_data_db()
        while any(True for _ in db.get_entry(uid)):
            uid = generate_id()

        # create empty entry
        db.write_entry({"_id": uid})
        # redirect to entry
        return redirect(f"{frontend.url_prefix}/{uid}", code=302)
    else:
        return render_template("pages/material.html")
