# Standard lib imports
from http import client
import unittest
from unittest.mock import patch

# Third party imports
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

# Project level imports
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.tasks.webhook_notification import update_failed_count, \
    notify_subscribed_accounts
from pywebhooks.utils.request_handler import RequestHandler


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingWebHookNotifications())
    return test_suite


class WhenTestingWebHookNotifications(unittest.TestCase):

    def setUp(self):
        pass

    def test_update_failed_count_exceptions(self):
        with patch.object(Interactions, 'get',
                          side_effect=RqlRuntimeError(None, None, None)):
            self.assertIsNone(update_failed_count(account_id='123'))

            with patch.object(Interactions, 'get',
                              side_effect=RqlDriverError(None)):
                self.assertIsNone(update_failed_count(account_id='123'))

    def test_update_failed_count(self):
        account_record = {
            'failed_count': 0
        }

        with patch.object(Interactions, 'get',
                          return_value=account_record) as \
                get_method:
            with patch.object(Interactions, 'update', return_value=None) as \
                    update_method:

                update_failed_count(
                    account_id='123',
                    increment_failed_count=True
                )

                get_method.assert_called_with(
                    DEFAULT_ACCOUNTS_TABLE,
                    record_id='123'
                )

                update_method.assert_called_with(
                    DEFAULT_ACCOUNTS_TABLE,
                    record_id='123',
                    updates={'failed_count': 1}
                )

                update_failed_count(
                    account_id='123',
                    increment_failed_count=False
                )

                update_method.assert_called_with(
                    DEFAULT_ACCOUNTS_TABLE,
                    record_id='123',
                    updates={'failed_count': 0}
                )

    @patch('pywebhooks.tasks.webhook_notification.update_failed_count')
    def test_notify_subscribed_accounts(self, update_failed_count_method):

        account_id = '123'
        update_failed_count_method.return_value = None
        request_handler_return = None, client.OK

        with patch.object(RequestHandler, 'post',
                          return_value=request_handler_return):

            notify_subscribed_accounts(event=None, event_data=None,
                                       secret_key=None, endpoint=None,
                                       account_id=account_id)

            update_failed_count_method.assert_called_with(
                account_id,
                increment_failed_count=False
            )

    @patch('pywebhooks.tasks.webhook_notification.update_failed_count')
    def test_notify_subscribed_accounts_endppoint_issue(
            self, update_failed_count_method):

        update_failed_count_method.return_value = None
        request_handler_return = None, client.INTERNAL_SERVER_ERROR

        with patch.object(RequestHandler, 'post',
                          return_value=request_handler_return):
            # Catch the raise
            try:
                notify_subscribed_accounts(event=None, event_data=None,
                                           secret_key=None, endpoint=None,
                                           account_id=None)
            except Exception as exc:
                self.assertEqual('Endpoint returning non HTTP 200 status. '
                                 'Actual code returned: 500', exc.args[0])
                self.assertRaises(Exception)
