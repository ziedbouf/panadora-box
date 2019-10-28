import os
import pandora

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from pandora.config import current_config
from pandora.utils.loggers import setup_logging
from .exceptions import ImproperlyConfigured

db = SQLAlchemy()
flask_bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_file):
    app = Flask(__name__)
    # load configuration
    config = current_config(config_file)
    root_path = os.path.dirname(os.path.dirname(pandora.__file__))
    logger_config_path = os.path.join(root_path, config.get('LOG_CONFIG'))
    setup_logging(logger_config_path, config.get('DEBUG'))

    # Check security key
    secret_key = config.get('SECRET_KEY')
    if not secret_key or len(secret_key) < 16:
        raise ImproperlyConfigured(
            'The SECRET_KEY must be set and longer than 16 chars.')

    app.config.from_mapping(config.to_dict())
    db.init_app(app)
    flask_bcrypt.init_app(app)
    login_manager.init_app(app)

    return app
