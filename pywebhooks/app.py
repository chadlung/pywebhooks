import falcon

from pywebhooks.log import get_logger, get_log_manager
from pywebhooks.util.config import ConfigurationError
from pywebhooks.config import load_pywebhooks_config
from pywebhooks.api.version.resources import VersionResource

_LOG = get_logger(__name__)


def start_up():
    config = load_pywebhooks_config()

    # Init logging
    logging_manager = get_log_manager()
    logging_manager.configure(config)

    _LOG.info('PyWebHooks Server Starting...')
    #print('Logging Verbosity: {}'.format(config.logging.verbosity))

    wsgi_app = api = falcon.API()
    api.add_route('/', VersionResource())
    return wsgi_app


application = start_up()

