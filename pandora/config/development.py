import os
from .base import BaseConfig, basedir


class Config(BaseConfig):
    DEBUG = True
    FLASK_DEBUG = True
    LOG_CONFIG = 'pandora/utils/logger_config.yml'

    # DB setting
    DB_NAME = 'db/pandora'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, '{}.db'.format(DB_NAME))

    # App secret - set this to random string >= 16 chars
    SECRET_KEY = 'secret123secret123secret123'

    # Enabled AUTH modules
    AUTH_MODULES = 'local,ldap'

    # Ldap config
    LDAP_URI = 'ldap://127.0.0.1'
