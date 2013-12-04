import os.path
import pynsive

from ConfigParser import ConfigParser


def _find_cfg_classes(module):
    def configuration_objects_only(cls):
        return issubclass(cls, ConfigurationPart)

    return pynsive.list_classes(module, configuration_objects_only)


def load_config(cfg_module_name, location, defaults=None):
    if not os.path.isfile(location):
        raise ConfigurationError(
            'Unable to locate configuration file: {}'.format(location))

    cfg = ConfigParser()
    cfg.read(location)

    return Configuration(_find_cfg_classes(cfg_module_name), cfg, defaults)


class ConfigurationError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Configuration(object):

    def __init__(self, cfg_cls_list, cfg, defaults):
        self._cfg_objects = dict()

        for cfg_cls in cfg_cls_list:
            cfg_object = cfg_cls(cfg, defaults)
            self._cfg_objects[cfg_object.name()] = cfg_object

    def __getattr__(self, name):
        return self._cfg_objects.get(name)


class ConfigurationPart(object):
    """
    A configuration part is an OO abstraction for a ConfigParser that allows
    for ease of documentation and usage of configuration options. All
    subclasses of ConfigurationPart must follow a naming convention. A
    configuration part subclass must start with the name of its section. This
    must then be followed by the word "Configuration." This convention results
    in subclasses with names similar to: CoreConfiguration and
    LoggingConfiguration.

    A configuration part subclass will have its section set to the lowercase
    name of the subclass sans the word such that a subclass with the name,
    "LoggingConfiguration" will reference the ConfigParser section "logging"
    when looking up options.
    """

    def __init__(self, cfg, defaults=None):
        self._cfg = cfg
        self._name = self.name()
        self._defaults = dict() if not defaults else defaults

    def __getattr__(self, name):
        return self.get(name)

    def _get_default(self, option):
        namespace = self._defaults.get(self._name)
        return namespace.get(option) if namespace else None

    def name(self):
        return type(self).__name__.replace('Configuration', '').lower()

    def options(self):
        return self._cfg.options(self._name)

    def has_option(self, option):
        return self._cfg.has_option(self._name, option)

    def get(self, option):
        if self.has_option(option):
            return self._cfg.get(self._name, option)
        else:
            return self._get_default(option)

    def getboolean(self, option):
        if self.has_option(option):
            return self._cfg.getboolean(self._name, option)
        else:
            return self._get_default(option)

    def getint(self, option):
        if self.has_option(option):
            return self._cfg.getint(self._name, option)
        else:
            return self._get_default(option)
