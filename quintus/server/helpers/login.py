from psycopg import Cursor

from .accounts import get_account_from_unique, update_last_login
from .password import hash_password
from .sessions import create_session, delete_session


"""
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: str):
    print()
    return User.get(user_id)
"""


def login_user(cursor: Cursor, unique: str, password: str) -> str:
    user = get_account_from_unique(cursor, unique)
    if user is None:
        print("no user")
        return None

    hased_password = hash_password(password, user["salt"])
    if hased_password != user["password"]:
        return None

    user_id = user["user_id"]
    session = create_session(cursor, user_id)
    update_last_login(cursor, user_id)
    return session


def logout_user(cursor: Cursor, user_id: int):
    delete_session(cursor, user_id)
    update_last_login(cursor, user_id)
