# Standard lib imports
# None

# Third-party imports
import rethinkdb as rethink
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

# Project-level imports
from pywebhooks import DEFAULT_DB_NAME, DEFAULT_TABLE_NAMES
from pywebhooks.utils.rethinkdb_helper import get_connection


def create_database():
    """
    Creates a new RethinkDB database with tables if it doesn't already exist
    """
    try:
        with get_connection() as conn:
            db_list = rethink.db_list().run(conn)

            if DEFAULT_DB_NAME not in db_list:
                # Default db doesn't exist so add it
                rethink.db_create(DEFAULT_DB_NAME).run(conn)

            table_list = rethink.db(DEFAULT_DB_NAME).table_list().run(conn)

            for table_name in DEFAULT_TABLE_NAMES:
                if table_name not in table_list:
                    # Add the missing table(s)
                    rethink.db(DEFAULT_DB_NAME).table_create(table_name)\
                        .run(conn)

    except (RqlRuntimeError, RqlDriverError) as err:
            print(err.message)
