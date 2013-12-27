"""
This module handles the loading of configuration settings for the application.
The module first loads default config values and then attempts to read
settings from a config file.
A PyWebHooksConfiguration object is created once and is provided by reference
to other modules through the get_config module.
"""

from ConfigParser import ConfigParser

_CONFIG_FILE = './pkg/layout/etc/pywebhooks/pywebhooks.conf'


_CFG_DEFAULTS = {
    'celery': {
        'broker_url': 'librabbitmq://guest@localhost//',
        'celeryd_concurrency': 2,
        'disable_rate_limits': True
    },
    'logging': {
        'console': True,
        'logfile': None,
        'verbosity': 'DEBUG'
    },
    'sqlalchemy': {
        'secret_key': 'thisCanbeWhatever',
        'database_uri': 'sqlite:///db.sqlite',
        'commit_on_teardown': True,
        'auth_token_expiration': 600
    }
}


class ConfigSection(object):
    """
    Class for a configuration section that allows for dynamic settings of
    options as attributes
    """
    def add_option(self, option, value):
        self.__setattr__(option, value)


class PyWebHooksConfiguration(object):
    """
    Class that holds all configuration settings as attributes.
    The class allows the loading of default config values from a dictionary
    and for loading of config values from a stdlib ConfigParser object.
    """
    def __init__(self, default_cfg):
        self.load_defaults(default_cfg)

    def load_defaults(self, default_cfg):
        """
        Set attributes from ConfigSection objects created from a dictionary
        of default config values
        """
        for section_name in default_cfg:
            section = ConfigSection()
            for option in default_cfg[section_name]:
                section.add_option(option, default_cfg[section_name][option])
            self.__setattr__(section_name, section)

    def load_config(self, cfg_parser):
        """
        Set attributes from ConfigSection objects created from a dictionary
        of default config values
        """
        for section_name in cfg_parser.sections():
            section = ConfigSection()
            for option in cfg_parser.options(section_name):
                section.add_option(
                    option, cfg_parser.get(section_name, option))
            self.__setattr__(section_name, section)


_cfg = PyWebHooksConfiguration(_CFG_DEFAULTS)


def load_config(config_file=_CONFIG_FILE):
    cfg_parser = ConfigParser()
    cfg_parser.read(config_file)
    _cfg.load_config(cfg_parser)


def get_config():
    load_config()
    return _cfg