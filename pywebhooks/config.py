from pywebhooks.util.config import (load_config, ConfigurationPart,
                               ConfigurationError)


_DEFAULTS = {
    'logging': {
        'console': True,
        'logfile': None,
        'verbosity': 'WARNING'
    }
}


def load_pywebhooks_config(location='/etc/pywebhooks/pywebhooks.conf'):
    return load_config('pywebhooks.config', location, _DEFAULTS)


class LoggingConfiguration(ConfigurationPart):
    """
    Class mapping for the pywebhooks logging configuration section.
    ::
        # Logging section
        [logging]
    """
    @property
    def console(self):
        """
        Returns a boolean representing whether or not pywebhooks should write
        to stdout for logging purposes. This value may be either True of False.
        If unset this value defaults to False.
        ::
            console = True
        """
        return self.get('console')

    @property
    def logfile(self):
        """
        Returns the log file the system should write logs to. When set,
        pywebhooks will enable writing to the specified file for logging
        purposes If unset this value defaults to None.
        ::
            logfile = /var/log/pywebhooks/pywebhooks.log
        """
        return self.get('logfile')

    @property
    def verbosity(self):
        """
        Returns the type of log messages that should be logged. This value may
        be one of the following: DEBUG, INFO, WARNING, ERROR or CRITICAL. If
        unset this value defaults to WARNING.
        ::
            verbosity = DEBUG
        """
        return self.get('verbosity')
