# Standard lib imports
import unittest
from unittest.mock import patch

# Third party imports
# None

# Project level imports
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.tasks.webhook_notification import update_failed_count


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingWebHookNotifications())
    return test_suite


class WhenTestingWebHookNotifications(unittest.TestCase):

    def setUp(self):
        pass

    def test_webhook_notifications(self):
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
