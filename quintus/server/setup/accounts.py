from psycopg import Connection
from quintus.server.helpers import create_roles, create_account
from pathlib import Path
import json


def setup_accounts(conn: Connection):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
            SELECT FROM
                pg_tables
            WHERE
                schemaname = 'public' AND
                tablename  = 'accounts'
            );
        """
        )
        # create Tables if not exists
        if not cur.fetchone()[0]:
            print("CREATE ACCOUNT TABLES")
            """
                user_id: 4B

                disable: 1B
                created_on: 8B
                lost_login: 8B
            """
            cur.execute(
                """
                CREATE TABLE accounts (
                    user_id serial PRIMARY KEY,
                    username VARCHAR ( 50 ) UNIQUE NOT NULL,
                    password CHAR ( 64 ) NOT NULL,
                    salt CHAR ( 64 ) NOT NULL,
                    email VARCHAR ( 255 ) UNIQUE NOT NULL,
                    disabled BOOLEAN DEFAULT FALSE,
                    created_on TIMESTAMP NOT NULL,
                    last_login TIMESTAMP
                );
            """
            )

            cur.execute(
                """
                CREATE TABLE roles(
                    role_id serial PRIMARY KEY,
                    role_name VARCHAR (255) UNIQUE NOT NULL
                );
            """
            )

            cur.execute(
                """
                CREATE TABLE account_roles (
                    user_id INT NOT NULL,
                    role_id INT NOT NULL,
                    grant_date TIMESTAMP,
                    PRIMARY KEY (user_id, role_id),
                    FOREIGN KEY (role_id)
                        REFERENCES roles (role_id),
                    FOREIGN KEY (user_id)
                        REFERENCES accounts (user_id)
                );
            """
            )
            storage = Path(__file__).parent / "data"
            roles_file = storage / "roles.json"

            with roles_file.open("r") as fp:
                roles = json.load(fp)
            create_roles(cur, roles)

            accounts_file = storage / "accounts.json"

            with accounts_file.open("r") as fp:
                accounts = json.load(fp)
            for account in accounts:
                create_account(cur, **account)
        conn.commit()
