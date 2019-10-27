from datetime import timedelta

import json
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    DEBUG = False
    FLASK_DEBUG = False
    SECRET_KEY = 'my_precious_secret_key'

    LOG_LEVEL = 'WARNING'
    LOG_CONFIG = 'panadora/utils/logger_config.yml'

    PANADORA_HOST = '0.0.0.0'
    PANADORA = 5000

    POOL_MAX_WORKER = 64

    # DB setting
    DB_NAME = "panadora"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, '{}.db'.format(DB_NAME))
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Kubespray setting
    KS_FILE_PATH = "/opt/panadora"
    KS_KUBESPRAY_PATH = './kubespray'
    KS_SSH_CMD = '/user/bin/ssh'
    KS_SSH_KEYGEN_CMD = "/usr/bin/ssh-keygen"
    KS_ANSIBLE_CMD = "/usr/bin/ansible"
    KS_ANSIBLE_PLAYBOOK_CMD = "/usr/bin/ansible-playbook"
    KS_DEFAULT_NAMESERVERS = "1.1.1.1,8.8.8.8"

    # KOPS setting
    # @TODO add the needed kops config
    KOPS_PATH = '/usr/local/bin/kops'
    KOPS_STATE_FILE = 'file:///etc/panadora/kops'

    # JWT auth options
    JWT_DEFAULT_REALM = 'Login Required'
    JWT_AUTH_URL_RULE = '/api/v1/auth'
    JWT_EXPIRATION_DELTA = timedelta(hours=1)
    JWT_AUTH_HEADER_PREFIX = 'Bearer'

    BCRYPT_ROUNDS = 12

    # Cluster statuses
    CLUSTER_ERROR_STATE = 'Error'
    CLUSTER_OK_STATE = 'OK'
    CLUSTER_PROVISIONING_STATE = 'Deploying'
    CLUSTER_DEPROVISIONING_STATE = 'Destroying'
    CLUSTER_UPDATING_STATE = 'Updating'
    CLUSTER_UNKNOWN_STATE = 'Unknown'

    CLUSTER_STATE_ON_LIST = True

    # Provisioner statuses
    PROVISIONER_ERROR_STATE = 'Error'
    PROVISIONER_OK_STATE = 'OK'
    PROVISIONER_UNKNOWN_STATE = 'Not Reachable'

    PROVISIONER_ENGINE_WHITELIST = None
    PROVISIONER_STATE_ON_LIST = True

    # Timeout for cluster operations (in seconds)
    PROVISIONER_TIMEOUT = 3600
    PROMETHEUS_WHITELIST = '127.0.0.0/8'

    # Enabled AUTH modules
    AUTH_MODULES = 'local'

    # Auth config
    LDAP_URI = 'ldap://127.0.0.1'
    # Creds for Panadora Read-only user
    LDAP_DN = 'cn=admin,dc=example,dc=org'
    LDAP_PASSWORD = 'heslo123'

    # MAIL Setting
    USER_EMAIL_SENDER_EMAIL = 'hello@panadora.io'

    @classmethod
    def get(cls, name, default=None):
        """ Emulate get method from dict """

        if hasattr(cls, name):
            return getattr(cls, name)
        else:
            return default

    @classmethod
    def to_dict(cls):
        """ Return dict of all uppercase attribute """
        res = {}

        for att_name in dir(cls):
            if att_name.isupper():
                res[att_name] = getattr(cls, att_name)

        return res

    @classmethod
    def setup_policies(cls):
        """ Read default policy file """

        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, 'policies/default_policy.json')
        with open(full_path, 'r') as fh:
            try:
                policy_string = fh.read()
                cls.DEFAULT_POLICIES = json.load(policy_string)
            except Exception:
                cls.DEFAULT_POLICIES = {}
