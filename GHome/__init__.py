import os
from flask import Flask

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "GHome.sqlite"),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from GHome import db

    db.init_app(app)

    from GHome import home, auth

    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)

    app.add_url_rule("/", endpoint="index")

    return app
