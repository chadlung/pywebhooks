# Standard lib imports
# None

# Third-party imports
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from werkzeug.security import generate_password_hash

# Project-level imports
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.utils.common import generate_key


def create_admin_account():
    """
    Creates a new admin account
    """
    try:
        original_api_key = generate_key()
        secret_key = generate_key()
        hashed_api_key = generate_password_hash(original_api_key)

        Interactions.insert(DEFAULT_ACCOUNTS_TABLE,
                            **{'username': 'admin',
                               'endpoint': '',
                               'is_admin': True,
                               'api_key': hashed_api_key,
                               'secret_key': secret_key})

        return {'api_key': original_api_key, 'secret_key': secret_key}
    except (RqlRuntimeError, RqlDriverError) as err:
        print(err.message)
