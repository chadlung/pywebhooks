import rethinkdb as rethink

from pywebhooks import DEFAULT_DB_NAME, RETHINK_PORT, \
    RETHINK_HOST, RETHINK_AUTH_KEY


def get_connection():
    return rethink.connect(
        host=RETHINK_HOST,
        port=RETHINK_PORT,
        auth_key=RETHINK_AUTH_KEY,
        db=DEFAULT_DB_NAME
    )
