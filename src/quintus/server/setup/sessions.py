from psycopg import Connection


def setup_sessions(conn: Connection):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
            SELECT FROM
                pg_tables
            WHERE
                schemaname = 'public' AND
                tablename  = 'sessions'
            );
        """
        )

        # create Tables if not exists
        if not cur.fetchone()[0]:
            cur.execute(
                """
                CREATE TABLE sessions (
                    token CHAR(255) UNIQUE NOT NULL,
                    user_id INT UNIQUE NOT NULL,
                    created_on TIMESTAMP NOT NULL
                );
            """
            )
    conn.commit()
