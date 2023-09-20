from flask import Blueprint, render_template, request, redirect
from quintus.io.mongo import MongoDataWriter
import uuid
import base64


material_page = Blueprint(
    "material_page",
    __name__,
    url_prefix="/data",
    static_folder="static",
    template_folder="templates",
)

db = MongoDataWriter(override=False)


def generate_id():
    identifier = uuid.uuid1()
    only_upper = base64.b32encode(identifier.bytes).decode("utf-8")
    short = only_upper[:8]
    return short


@material_page.route("/", defaults={"materialID": "all"}, methods=["GET"])
@material_page.route("/<materialID>")
def change(materialID):
    if materialID == "all":
        materials = []
        for entry in db.document.find(dict()):
            material = dict()
            material["id"] = entry["_id"]
            material["url"] = f"{material_page.url_prefix}/{material['id']}"
            materials.append(material)
        return render_template("pages/materials.html", materials=materials)
    elif materialID == "new":
        # create short!!! uuid
        uid = generate_id()
        # check if already exists if not generate again
        while any(True for _ in db.get_entry(uid)):
            uid = generate_id()

        # create empty entry
        db.write_entry({"_id": uid})
        # redirect to entry
        return redirect(f"{material_page.url_prefix}/{uid}", code=302)
    else:
        print(db.get_entry(materialID))
        return render_template("pages/material.html")


@material_page.route("/<materialID>", methods=["POST"])
def handle_data(materialID):
    old_data = db.document.find_one({"_id": materialID})
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        new_data = request.json
        result = db.document.update_one({"_id": materialID}, {"$set": new_data})
        print(result.acknowledged)
        if result.acknowledged:
            return new_data, 201, {"Content-Type": "application/json"}
        else:
            return old_data, 404, {"Content-Type": "application/json"}
    elif content_type == "application/x-www-form-urlencoded":
        data = request.form
        return data

    return "<p>Success!</p>"
