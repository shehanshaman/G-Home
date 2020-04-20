import sqlite3

import click
from flask import current_app
from flask import g
from flask.cli import with_appcontext
from pathlib import Path

ROOT_PATH = Path.cwd()
MAIL_PATH = ROOT_PATH / "GHome" / "mail"


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """

    if "db" not in g:
        GeNet_app  = current_app.config['APP_ALZ']
        mysql = GeNet_app.db
        g.db = mysql.get_db()
        # cur = mysql.get_db().cursor()
        # g.db = cur
        # g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    # if db is not None:
    #     db.close()
    #     print("db.close")


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    # init_db()
    add_mail_templates()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def add_mail_templates():
    db = get_db()
    cur = db.cursor()

    subjects = ["verify", "reset"]
    for subject in subjects:
        file_name = MAIL_PATH / (subject + '_mail.html')
        f = open(file_name, "r")
        message = f.read()
        cur.execute(
            "INSERT INTO mail_template (subject, message) VALUES (%s, %s)",
            (subject, message),
        )
    db.commit()
