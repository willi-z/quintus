from quintus.server.helpers import get_user_db, close_user_db
from .accounts import setup_accounts
from .sessions import setup_sessions
import click

# https://flask.palletsprojects.com/en/2.2.x/tutorial/database/


def init_dbs():
    conn = get_user_db()
    setup_accounts(conn)
    setup_sessions(conn)


def close_dbs(event=None):
    close_user_db(event)


@click.command("init-db")
def init_dbs_command():
    init_dbs()
    click.echo("intitialized the database.")


def init_app(app):
    # https://flask.palletsprojects.com/en/2.2.x/tutorial/database/
    app.teardown_appcontext(close_dbs)
    with app.app_context():
        init_dbs()
    app.cli.add_command(init_dbs_command)
