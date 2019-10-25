from .base import BaseConfig


class Config(BaseConfig):
    DEBUG = False
    LOG_CONFIG = 'panadora/utils/logger_config.yml'

    # App secret - set this to random string >= 16 chars
    SECRET_KEY = 'secret123secret123secret123'

    # Enabled AUTH modules
    AUTH_MODULES = 'local,ldap'

    # Ldap config
    LDAP_URI = 'ldap://127.0.0.1'