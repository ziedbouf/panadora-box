from distutils import util
import importlib
import logging
import os
import re

logger = logging.getLogger('panadora_api')
CONFIG_FILE_DEFAULT = 'config/development.py'


def select_file(config_file=None):
    """Select configuration file

    Keyword Arguments:
        config_file {str} -- config file name    (default: {None})

    Returns:
        str -- Config file from env. variables or default config file 'config/dev.py'
    """
    if not config_file:
        config_file = os.environ.get(
            'PANADORA_CONFIG_FILE', CONFIG_FILE_DEFAULT)
        logger.debug('Config file from env variable {}'.format(config_file))

    return config_file


def apply_env_changes(config, prefix='PANADORA_'):
    """Read env variables strting with prefix and apply them to existing configuration

    Arguments:
        config {obj} -- Configuration objct. this configuration will updated

    Keyword Arguments:
        prefix {str} -- Prefix for enviroment variables to select. (default: {'PANADORA_'})
    """
    for name, value in os.environ.items():
        if name.startswith(prefix):
            config_key_name = name[len(prefix):]

            if re.search('(?i)true|(?i)false', value):
                value = util.strtobool(value)

            setattr(config, config_key_name, value)


def current_config(config_file=None):
    if config_file == None:
        config_file = CONFIG_FILE_DEFAULT

    read_file = select_file(config_file)
    logger.debug('Loading configuration from {}'.format(read_file))

    module_name = read_file.replace('/', '.').replace('.py', '')
    module = importlib.import_module('panadora.{}'.format(module_name))
    config = getattr(module, 'Config')
    apply_env_changes(config)
    setattr(config, 'source_file', read_file)

    return config
