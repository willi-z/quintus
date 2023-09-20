from flask import current_app, g
import psycopg
from quintus.io.mongo import MongoDataWriter
import base64


def get_user_db():
    if "user_db" not in g:
        g.user_db = psycopg.connect(
            host="localhost",
            port=int(current_app.config["DB_USER.PORT"]),
            dbname=current_app.config["DB_USER.DB_NAME"],
            user=base64.b64decode(current_app.config["DB_USER.USER"]).decode(),
            password=base64.b64decode(current_app.config["DB_USER.PASSWORD"]).decode(),
        )
        # g.db.row_factory = sqlite3.Row

    return g.user_db


def close_user_db(event=None):
    db = g.pop("user_db", None)

    if db is not None:
        db.close()


def get_data_db():
    if "data_db" not in g:
        g.data_db = MongoDataWriter(override=False)
        # g.db.row_factory = sqlite3.Row
    return g.data_db


def close_data_db(event=None):
    db = g.pop("data_db", None)

    if db is not None:
        db.client.close()
