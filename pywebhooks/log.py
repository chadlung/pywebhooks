import logging


def configure_logging(cfg):
    logger = logging.getLogger()
    logger.setLevel(cfg.logging.verbosity)

    try:
        if cfg.logging.logfile:
            logger.addHandler(logging.FileHandler(cfg.logging.logfile))
    except AttributeError:
        pass
    if bool(cfg.logging.console):
        logger.addHandler(logging.StreamHandler())
