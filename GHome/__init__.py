import os
from flask import Flask

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "GHome.sqlite"),
        BLYNK_HOST = "http://188.166.206.43/",
        # BLYNK_HOST = 'http:127.0.0.1:8080/'
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

    return app
