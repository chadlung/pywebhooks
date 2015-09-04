DEFAULT_DB_NAME = 'pywebhooks'
DEFAULT_ACCOUNTS_TABLE = 'accounts'
DEFAULT_REGISTRATIONS_TABLE = 'registrations'
DEFAULT_TRIGGERED_TABLE = 'triggered_webhooks'
DEFAULT_SUBSCRIPTIONS_TABLE = 'subscriptions'

DEFAULT_TABLE_NAMES = [
    DEFAULT_ACCOUNTS_TABLE,
    DEFAULT_REGISTRATIONS_TABLE,
    DEFAULT_TRIGGERED_TABLE,
    DEFAULT_SUBSCRIPTIONS_TABLE
]

# This is the timeout for the response time from the client's endpoint. This is
# used when validating a new account or they attempt to change a secret or
# api key and in sending out webhook events. This should be a low value and end
# users should be aware of this time (in seconds) in which to respond.
REQUEST_TIMEOUT = 5.0

# Retry a failed webhook notification to an endpoint in 2 minutes
DEFAULT_RETRY = 120
DEFAULT_FINAL_RETRY = 3600  # On the final retry, try again in an hour

# How many times a webhook post can fail to contact the endpoint before
# its ignored
MAX_FAILED_COUNT = 250

RETHINK_HOST = 'localhost'
RETHINK_PORT = 28015
RETHINK_AUTH_KEY = ''

CELERY_BROKER_URL = 'redis://localhost:6379/0'
