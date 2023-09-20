from flask import Blueprint, request
from quintus.server.helpers.db import get_data_db


data = Blueprint("data", __name__, url_prefix="/data")


@data.route("/", methods=["GET"])
def get_data():
    if request.args.get("all") is not None:
        db = get_data_db()
        data = {}
        for collection in db.list_collection_names():
            data[collection] = []
            cursor = db[collection].find()
            for document in cursor:
                data[collection].append(document)

        return data, 200, {"Content-Type": "application/json"}
    elif request.args.get("dump") is not None:
        pass


@data.route("/<document>/<id>", methods=["GET"])
def request_entry(document: str, id: str):
    pass


@data.route("/<collection>/<id>", methods=["POST"])
def create_entry(collection: str, id: str):
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return "Wrong Content-Type", 400
    data = request.json
    # validate data

    db = get_data_db()
    # check if enty exists
    if collection in db.list_collection_names():
        if db[collection].find_one({"_id": id}) is not None:
            # maybe redirect to new id?
            return "An Entry already exists!", 400
    else:
        db.create_collection(collection)

    data["_id"] = id
    db[collection].insert_one(data)

    return "Created Entry", 200


@data.route("/<collection>/<id>", methods=["UPDATE"])
def update_entry(collection: str, id: str):
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return "Wrong Content-Type!", 400
    new_data = request.json
    db = get_data_db()
    if collection not in db.list_collection_names():
        return "Could not find collection!", 400

    collection = db[collection]
    old_data = collection.find_one({"_id": id})
    if old_data is None:
        return "Could not find document!", 400

    result = collection.update_one({"_id": id}, {"$set": new_data})
    if result.acknowledged:
        return new_data, 201, {"Content-Type": "application/json"}
    else:
        return old_data, 404, {"Content-Type": "application/json"}
