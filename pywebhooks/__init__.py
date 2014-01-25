from celery import Celery
from oslo.config import cfg

from pywebhooks import log


opt_celery_group = cfg.OptGroup(name='celery',
                                title='Celery Configuration')

celery_opts = [
    cfg.StrOpt('broker_url', default='librabbitmq://guest@localhost//',
               help='RabbitMQ broker URL'),
    cfg.IntOpt('celeryd_concurrency', default=2,
               help='Celeryd Concurrency'),
    cfg.BoolOpt('disable_rate_limits', default=True,
                help='Disable rate limits')
]

opt_logging_group = cfg.OptGroup(name='logging',
                                 title='Logging Configuration')

logging_opts = [
    cfg.BoolOpt('console', default=True,
                help='Whether to output to the console'),
    cfg.StrOpt('logfile', default='/var/log/pywebhooks/pywebhooks.log',
               help='Location of the log file'),
    cfg.StrOpt('verbosity', default="DEBUG",
               help='Log verbosity setting')
]

opt_sqlalchemy_group = cfg.OptGroup(name='sqlalchemy',
                                    title='SQLAlchemy Configuration')

sqlalchemy_opts = [
    cfg.StrOpt('secret_key', default='thisCanbeWhatever',
               help='This should be a random string'),
    cfg.StrOpt('database_uri', default='sqlite:///db.sqlite',
               help='Database URI'),
    cfg.BoolOpt('commit_on_teardown', default=True,
                help='Commit on Teardown'),
    cfg.IntOpt('auth_token_expiration', default=600,
               help='Auth token expiration time')
]

CONF = cfg.CONF

CONF.register_group(opt_celery_group)
CONF.register_opts(celery_opts, opt_celery_group)

CONF.register_group(opt_logging_group)
CONF.register_opts(logging_opts, opt_logging_group)

CONF.register_group(opt_sqlalchemy_group)
CONF.register_opts(sqlalchemy_opts, opt_sqlalchemy_group)

CONF(config_files=['./pkg/layout/etc/pywebhooks/pywebhooks.conf'])

log.configure_logging(CONF)

CELERY = Celery('pywebhooks', broker=CONF.celery.broker_url)
CELERY.conf.CELERYD_CONCURRENCY = CONF.celery.celeryd_concurrency
CELERY.conf.CELERY_DISABLE_RATE_LIMITS =\
    CONF.celery.disable_rate_limits
CELERY.conf.CELERY_TASK_SERIALIZER = 'json'
CELERY.conf.CELERYD_HIJACK_ROOT_LOGGER = False