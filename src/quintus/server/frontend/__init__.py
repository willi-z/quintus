from flask import Blueprint, request, render_template, redirect, abort
import flask_login as fl
from quintus.server.helpers import login_user, get_user_db, get_data_db


frontend = Blueprint(
    "frontend",
    __name__,
    template_folder="templates",
)


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
            user = login_user(cur, unique, password)
            fl.login_user(user)

        # if token is None:
        #     return abort(401)
        # session["token"] = token
        return redirect("/")
    return render_template("pages/login.html")


@frontend.route("/logout")
@fl.login_required
def logout():
    fl.logout_user()
    return redirect("/")


@frontend.route("/overview")
@fl.login_required
def overview():
    materials = []
    for entry in get_data_db().document.find(dict()):
        material = dict()
        material["id"] = entry["_id"]
        material["url"] = f"/api/data/{material['id']}"
        materials.append(material)
    print(materials)
    return render_template("pages/overview.html", materials=materials)


@frontend.route("/data/<collection>/<documentID>")
def get_material(collection, documentID):
    if collection == "material":
        return render_template("pages/material.html")
    return "NOT FOUND"
