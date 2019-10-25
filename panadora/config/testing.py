import os
from .base import BaseConfig, basedir


class Config(BaseConfig):
    DEBUG = True
    TESTING = True
    LOG_CONFIG = 'panadora/utils/logger_config.yml'

    # DB setting
    DB_NAME = 'db/t_panadora'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '{}.db'.format(DB_NAME))

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # No need for secure key in testing config
    SECRET_KEY = 'my_precious'

    # Enabled AUTH modules
    AUTH_MODULES = 'local,ldap'

    # Ldap config
    LDAP_URI = 'ldap://127.0.0.1'