# Standard lib imports
from http import client
import logging

# Third-party imports
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

# Project-level imports
from pywebhooks.app import CELERY
from pywebhooks import DEFAULT_RETRY, DEFAULT_FINAL_RETRY, REQUEST_TIMEOUT, \
    DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.utils.common import create_signature
from pywebhooks.utils.request_handler import RequestHandler


_LOG = logging.getLogger(__name__)


def update_failed_count(account_id=None, increment_failed_count=False):
    """
    Update the failed_count field on the user's account
    """
    try:
        # Get the failed_count value
        account_record = Interactions.get(
            DEFAULT_ACCOUNTS_TABLE, record_id=account_id)
        failed_count = int(account_record['failed_count'])

        if increment_failed_count:
            failed_count += 1
        else:
            failed_count = 0

        Interactions.update(DEFAULT_ACCOUNTS_TABLE, record_id=account_id,
                            updates={'failed_count': failed_count})
    except (RqlRuntimeError, RqlDriverError, Exception):
        pass


# Running the Worker from the project root:
#
# celery -A pywebhooks.tasks.webhook_notification worker --loglevel=info
#
@CELERY.task(bind=True, serializer='json', max_retries=3, ignore_result=True)
def notify_subscribed_accounts(self, event=None, event_data=None,
                               secret_key=None, endpoint=None,
                               account_id=None):
    """
    Send Webhook requests to all subscribed accounts
    """
    signature = create_signature(secret_key, event_data)

    request_handler = RequestHandler(
        verify_ssl=False, request_timeout=REQUEST_TIMEOUT)

    try:
        _, status_code = request_handler.post(
            url=endpoint,
            json_payload=event_data, event=event,
            signature=signature)

        # We don't care about anything but the return status code
        if client.OK != status_code:
            raise Exception('Endpoint returning non HTTP 200 status. '
                            'Actual code returned: {0}'.format(status_code))

        if client.OK == status_code:
            # Failed count will reset on a good contact
            update_failed_count(account_id, increment_failed_count=False)

    except Exception as exc:
        update_failed_count(account_id, increment_failed_count=True)

        if self.request.retries == 3:
            raise self.retry(exc=exc, countdown=DEFAULT_FINAL_RETRY)
        else:
            raise self.retry(exc=exc, countdown=DEFAULT_RETRY)
