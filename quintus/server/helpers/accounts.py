from datetime import datetime, timezone
from psycopg import Cursor


def create_roles(cursor: Cursor, roles: list[str]):
    entries = []
    for role in roles:
        entries.append("('" + role + "')")

    entries = ",".join(entries)

    cursor.execute(f"INSERT INTO roles (role_name) VALUES {entries};")


def create_account(
    cursor: Cursor, username: str, email: str, password: str, salt: str, roles: None
):
    utc_dt = datetime.now(timezone.utc)
    created = utc_dt.isoformat()
    result = cursor.execute(
        """
    INSERT INTO accounts (username, password, salt, email, created_on, last_login)
    VALUES (%(username)s, %(password)s, %(salt)s, %(email)s, %(created)s, %(created)s)
    RETURNING user_id;
    """,
        {
            "username": username,
            "password": password,
            "salt": salt,
            "email": email,
            "created": created,
        },
    )
    user_id = result.fetchone()[0]

    if roles is None:
        return

    content = []
    for role in roles:
        content.append(f"({user_id},{role})")

    cursor.execute(
        "INSERT INTO account_roles (user_id, role_id) VALUES " + ",".join(content) + ";"
    )


def get_account_from_id(cursor: Cursor, unique_identifier: str):
    cursor.execute("SELECT * FROM accounts WHERE user_id=%s;", [unique_identifier])
    user_response = cursor.fetchone()
    if user_response is None:
        return None

    cursor.execute(
        "SELECT role_id FROM account_roles WHERE user_id=%s;", [unique_identifier]
    )
    role_response = cursor.fetchall()
    roles = []
    if role_response is not None:
        for role in role_response:
            roles.append(role[0])

    return {
        "user_id": user_response[0],
        "username": user_response[1],
        "password": user_response[2],
        "salt": user_response[3],
        "email": user_response[4],
        "disabled": user_response[5],
        "created_on": user_response[6],
        "last_login": user_response[7],
        "roles": roles,
    }


def get_account_from_unique(cursor: Cursor, unique_identifier: str):
    if "@" in unique_identifier:
        cursor.execute("SELECT * FROM accounts WHERE email=%s;", [unique_identifier])
    else:
        cursor.execute("SELECT * FROM accounts WHERE username=%s;", [unique_identifier])

    response = cursor.fetchone()
    if response is None:
        return None
    return {
        "user_id": response[0],
        "username": response[1],
        "password": response[2],
        "salt": response[3],
        "email": response[4],
        "disabled": response[5],
        "created_on": response[6],
        "last_login": response[7],
    }


def update_role(cursor: Cursor, user_id: int, roles: list[int] = None):
    if roles is None or len(roles) == 0:
        cursor.execute("DELETE * FROM account_roles WHERE user_id=%s;", [user_id])
        return

    content = []
    for role in roles:
        content.append(f"({user_id},{role})")
    content = ",".join(content)
    cursor.execute(
        """
            BEGIN;
            DELETE FROM account_roles WHERE user_id=%(user_id)s;
            INSERT INTO account_roles (user_id, role_id) VALUES %(content)s;
            COMMIT;
            """,
        {"user_id": user_id, "content": content},
    )


def update_last_login(cursor: Cursor, user_id: int):
    utc_dt = datetime.now(timezone.utc)
    last_login = utc_dt.isoformat()
    cursor.execute(
        "UPDATE accounts SET last_login=%(last_login)s WHERE user_id=%(user_id)s;",
        {"last_login": last_login, "user_id": user_id},
    )
