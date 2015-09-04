# Standard lib imports
# None

# Third-party imports
import rethinkdb as rethink
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

# Project-level imports
from pywebhooks import DEFAULT_DB_NAME
from pywebhooks.utils.rethinkdb_helper import get_connection


def drop_database():
    """
    Deletes the RethinkDB database
    """
    try:
        with get_connection() as conn:
            rethink.db_drop(DEFAULT_DB_NAME).run(conn)
    except (RqlRuntimeError, RqlDriverError) as err:
            print(err.message)
