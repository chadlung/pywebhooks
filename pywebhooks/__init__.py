from celery import Celery

from pywebhooks import log, config


CONFIG = config.get_config()
log.configure_logging(CONFIG)

CELERY = Celery('pywebhooks', broker=CONFIG.celery.broker_url)
CELERY.conf.CELERYD_CONCURRENCY = CONFIG.celery.celeryd_concurrency
CELERY.conf.CELERY_DISABLE_RATE_LIMITS =\
    CONFIG.celery.disable_rate_limits
CELERY.conf.CELERY_TASK_SERIALIZER = 'json'
CELERY.conf.CELERYD_HIJACK_ROOT_LOGGER = False