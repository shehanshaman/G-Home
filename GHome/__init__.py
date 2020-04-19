import os
from flask import Flask

from apscheduler.schedulers.background import BackgroundScheduler

from GHome.classes.app_alz import Alz


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "GHome.sqlite"),
        # BLYNK_HOST = "http://188.166.206.43/",
        BLYNK_HOST = 'http://127.0.0.1:5555/',
        SCHEDULER = BackgroundScheduler(),

        SCHEDULER_STATE = 0,

        APP_ALZ=Alz(),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from GHome import db
    from flask_mail import Mail

    db.init_app(app)

    mail = Mail()
    mail_settings = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": 'shamanmario95@gmail.com',
        "MAIL_PASSWORD": 'mniShehan'
    }
    app.config.update(mail_settings)
    mail.init_app(app)

    app.config["APP_ALZ"].mail = mail

    from GHome import home, auth, admin

    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)

    app.add_url_rule("/", endpoint="index")

    return app
