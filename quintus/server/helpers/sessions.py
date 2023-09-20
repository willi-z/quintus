from psycopg import Cursor, sql
from datetime import datetime, timezone
import hashlib


def create_session(cursor: Cursor, user_id: int):
    utc_dt = datetime.now(timezone.utc)
    created = utc_dt.isoformat()
    token = str(user_id) + created
    for _ in range(2):
        m = hashlib.sha256(token.encode())
        token = m.hexdigest()
    cursor.execute(
        sql.SQL(
            """
        BEGIN;
        DELETE FROM sessions WHERE user_id={user_id};
        INSERT INTO sessions (token, user_id, created_on) VALUES
        ({token}, {user_id}, {created});
        COMMIT;"""
        ).format(
            **{
                "user_id": sql.Literal(user_id),
                "token": sql.Literal(token),
                "created": created,
            }
        )
    )

    return token


def delete_session(cursor: Cursor, user_id: int):
    cursor.execute(
        """
            DELETE FROM sessions WHERE user_id=%s;
        """,
        user_id,
    )


def get_user_id_from_session(cursor: Cursor, token: str):
    cursor.execute(
        "SELECT (user_id, created_on) FROM sessions WHERE token=%(token)s;",
        {"token": token},
    )
    result = cursor.fetchone()
    if result is None:
        return None
    else:
        user_id, created_on = result[0]
        last = datetime.strptime(created_on, "%Y-%m-%d %H:%M:%S.%f")
        last = last.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        duration = (now - last).total_seconds() / 60.0
        if duration >= 60:
            return None
        return user_id
