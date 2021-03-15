import logging

from flask import Flask

from . import config


def create_app():
    logging.basicConfig(level=config.LOG_LEVEL)

    app = Flask(__name__)

    from .admin import bp as admin_bp
    from .api import bp as api_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    return app
