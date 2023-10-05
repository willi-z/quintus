from flask import Blueprint, request
from quintus.server.helpers.db import get_data_db
import uuid
import base64


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


@data.route("/<collection>/<id>", methods=["GET"])
def request_entry(collection: str, id: str):
    db = get_data_db()

    if id == "new":
        id = generate_id()
        while db[collection].find_one({"_id": id}) is not None:
            id = generate_id()
        return (
            {"meta": {"id": id, "collection": collection}},
            300,
            {"Content-Type": "application/json"},
        )

    if collection not in db.list_collection_names():
        return "Could not find collection!", 404

    result = db[collection].find_one({"_id": id})
    if result is None:
        return "No Entry with this ID was found!", 404

    return result, 200, {"Content-Type": "application/json"}


def generate_id():
    identifier = uuid.uuid1()
    only_upper = base64.b32encode(identifier.bytes).decode("utf-8")
    short = only_upper[:8]
    return short


@data.route("/<collection>/<id>", methods=["POST"])
def create_entry(collection: str, id: str):
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return "Wrong Content-Type", 400
    data = request.json
    # validate data

    db = get_data_db()
    # check if enty exists
    if collection not in db.list_collection_names():
        db.create_collection(collection)

    if id == "new":
        id = generate_id()
        while db[collection].find_one({"_id": id}) is not None:
            id = generate_id()
    else:
        if db[collection].find_one({"_id": id}) is not None:
            return "An Entry with this ID already exists!", 404

    data["_id"] = id
    db[collection].insert_one(data)
    data["meta"] = {"id": id, "collection": collection}

    return data, 200, {"Content-Type": "application/json"}


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


@data.route("/<collection>/<id>", methods=["DELETE"])
def delete_entry(collection: str, id: str):
    db = get_data_db()
    if collection not in db.list_collection_names():
        return "Could not find collection!", 400

    collection = db[collection]
    data = collection.find_one({"_id": id})
    if data is None:
        return "Could not find document!", 400
    result = collection.delete_one({"_id": id})
    if result.acknowledged:
        return {}, 201, {"Content-Type": "application/json"}
    else:
        return (
            data,
            404,
        )
