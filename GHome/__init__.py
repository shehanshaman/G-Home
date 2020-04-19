import os
from flask import Flask

import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "GHome.sqlite"),
        BLYNK_HOST = "http://188.166.206.43/",
        # BLYNK_HOST = 'http:127.0.0.1:8080/'
        SCHEDULER = BackgroundScheduler(),

        SCHEDULER_STATE = 0,
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from GHome import db

    db.init_app(app)

    from GHome import home, auth, admin

    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)

    app.add_url_rule("/", endpoint="index")


    # scheduler.add_job(func=print_date_time, trigger="interval", seconds=3)
    # scheduler.start()

    return app
