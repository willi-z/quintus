from flask import Blueprint, request
from quintus.server.helpers import get_user_db, get_account_from_id


user = Blueprint("user", __name__, url_prefix="/user")


@user.route("/", methods=["GET"])
def get_user():
    if request.args.get("all") is not None:
        conn = get_user_db()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id from accounts;")
            result = cur.fetchall()
            users = []
            for id in result:
                users.append(get_account_from_id(cur, id[0]))
            return users
    return "", 404
