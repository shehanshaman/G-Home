import functools
import os
import random

from datetime import datetime


from flask import Blueprint, current_app
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from GHome.db import get_db
from pathlib import Path
from flask_mail import Message
import string

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )

@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        given_name = request.form["given_name"]

        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif (
            db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            is not None
        ):
            error = "User {0} is already registered.".format(username)

        if error is None:
            # the name is available, store it in the database and go to
            # the login page

            create_user_db(db, username, password, given_name, '', 0)
            if "@" in username:
                user_id = UserData.get_user_id(username)
                verify_key = randomString()
                db.execute(
                    "INSERT INTO verify (user_id, subject, verify_key) VALUES (?, ?, ?)",
                    (user_id, 'verify', verify_key),
                )
                db.commit()
                url = "http://" + str(request.host) + "/auth/verify/?id=" + str(user_id) + "&key=" + verify_key
                send_mail("verify", url, username, "Verify email address")

            message  = given_name + ", Your account created. Verify your email"
            flash(message)
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
        elif user["is_verified"] == 0:
            error = "Your account not verified, check email."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            update_last_login(db, user["id"])
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))

@bp.route("/glogin/", methods=["POST"])
def glogin():
    email = request.form["email"]
    given_name = request.form["given_name"]
    profile_id = request.form["profile_id"]
    image_url = request.form["image_url"]

    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE username = ?", (email,)
    ).fetchone()

    if user is None:
        # Register User
        create_user_db(db, email, profile_id, given_name, image_url, 2)
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (email,)
        ).fetchone()

    else:
        # Update user last login
        update_last_login(db, user["id"])

    session.clear()
    session["user_id"] = user["id"]

    return redirect(url_for("index"))

@bp.route("/verify/", methods=["GET"])
def verify():
    user_id = request.args.get('id')
    verify_key = request.args.get('key')

    db = get_db()
    verify_data = db.execute(
        "SELECT * FROM verify WHERE user_id = ? AND subject = 'verify'", (user_id,)
    ).fetchone()

    e = ["Not Found",[]]

    if verify_data is None:
        e[1].append("Not registered user.")

    elif verify_key == verify_data['verify_key']:
        db.execute(
            "UPDATE user SET is_verified = ? WHERE id = ?",
            (1, user_id),
        )
        db.commit()

        db.execute(
            "DELETE FROM verify WHERE user_id = ? AND subject = 'verify'",
            (user_id),
        )
        db.commit()
        flash("Your email has been verified.")
        return redirect(url_for("auth.login"))

    else:
        e[1].append("Wrong Key.")

    return render_template("error.html", errors=e)

@bp.route("/reset", methods = ["POST", "GET"])
def reset_request():

    if request.method == "POST":
        username = request.form["username"]
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE username = ? AND is_verified = 1", (username,)
        ).fetchone()

        if user is None:
            flash("Wrong username.")
            return render_template("auth/reset_request.html")

        user_id = user["id"]

        verify_key = randomString()

        db.execute(
            "INSERT INTO verify (user_id, subject, verify_key) VALUES (?, ?, ?)",
            (user_id, 'reset', verify_key),
        )
        db.commit()
        url = "http://" + str(request.host) + "/auth/reset/?id=" + str(user_id) + "&key=" + verify_key
        send_mail("reset", url, username, "Reset Password G-Home")

        message = "Please, check your email."
        flash(message)

        return redirect(url_for('auth.login'))

    return render_template("auth/reset_request.html")

@bp.route("/reset/", methods = ["GET", "POST"])
def reset_key_verify():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #Update password
        db = get_db()
        db.execute(
            "UPDATE user SET password = ? WHERE username = ?",
            (generate_password_hash(password), username),
        )
        db.commit()

        #Get user id
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        user_id = int(user['id'])

        #Delete query in verify
        db.execute(
            "DELETE FROM verify WHERE user_id = ? AND subject = 'reset'",
            (user_id,)
        )
        db.commit()

        flash("Your password has been reset.")
        return redirect(url_for("auth.login"))


    user_id = request.args.get('id')
    verify_key = request.args.get('key')

    db = get_db()
    verify_data = db.execute(
        "SELECT * FROM verify WHERE user_id = ? AND subject = 'reset' ORDER BY id DESC", (user_id,)
    ).fetchone()

    if verify_data is None:
        flash("You don't request for reset.")
        return redirect(url_for("auth.login"))

    elif verify_key == verify_data['verify_key']:

        flash("Your email has been verified, Enter new password.")

        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()

        return render_template("auth/reset.html", email = user["username"])

    else:
        flash("Wrong url for rest verification.")
        return redirect(url_for("auth.login"))

def create_user_db(db, username, password, given_name, image_url, is_verified):
    db.execute(
        "INSERT INTO user (username, password, given_name, image_url, last_login, is_verified) VALUES (?, ?, ?, ?, ?,?)",
        (username, generate_password_hash(password), given_name, image_url, datetime.now(), is_verified),
    )
    db.commit()

    return True

def update_last_login(db, user_id):
    db.execute(
        "UPDATE user SET last_login = ? WHERE id = ?",
        (datetime.now(), user_id),
    )
    db.commit()

def send_mail(subject, url, recipient, senders_subject):
    msg = Message(senders_subject,
                  sender="no-reply@GeNet.com",
                  recipients=[recipient])

    message = get_mail_message(subject)
    message = message.replace("{{action_url}}", url)
    msg.html = message
    mail = current_app.config["APP_ALZ"].mail
    s = mail.send(msg)

    return s

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def get_mail_message(subject):
    db = get_db()
    m = db.execute(
        "SELECT message FROM mail_template WHERE subject = ?",
        (subject,),
    ).fetchone()
    return m['message']

class UserData:

    def get_user_id(username):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()
        if user is not None:
            return user["id"]
        return None