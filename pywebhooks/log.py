import logging

_LOG_LEVEL_NOTSET = 'NOTSET'


def get_logger(logger_name):
    return _LOGGING_MANAGER.get_logger(logger_name)


def get_log_manager():
    return _LOGGING_MANAGER


class LoggingManager(object):

    def __init__(self):
        self._root_logger = logging.getLogger()
        self._handlers = list()

    def _add_handler(self, handler):
        self._handlers.append(handler)
        self._root_logger.addHandler(handler)

    def _clean_handlers(self):
        [self._root_logger.removeHandler(hdlr) for hdlr in self._handlers]
        del self._handlers[:]

    def configure(self, cfg):
        self._clean_handlers()

        # Configuration handling
        self._root_logger.setLevel(cfg.logging.verbosity)

        if cfg.logging.logfile:
            self._add_handler(logging.FileHandler(cfg.logging.logfile))
        if cfg.logging.console:
            self._add_handler(logging.StreamHandler())

    def get_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(_LOG_LEVEL_NOTSET)
        return logger

globals()['_LOGGING_MANAGER'] = LoggingManager()
