# Standard lib imports
import unittest
from unittest.mock import patch

# Third party imports
# None

# Project level imports
from pywebhooks import DEFAULT_REGISTRATIONS_TABLE, \
    DEFAULT_SUBSCRIPTIONS_TABLE, DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.api.handlers.resources_handler import \
    registration_id_exists, lookup_subscription_id, lookup_registration_id, \
    lookup_account_id


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingResourcesHandler())
    return test_suite


class WhenTestingResourcesHandler(unittest.TestCase):

    def setUp(self):
        pass

    def test_registration_id_exists(self):
        with patch.object(Interactions, 'query', return_value=True) as \
                query_method:

            self.assertTrue(registration_id_exists('123'))

            query_method.assert_called_with(
                DEFAULT_REGISTRATIONS_TABLE,
                filters={'id': '123'}
            )

        with patch.object(Interactions, 'query', return_value=False) as \
                query_method:

            self.assertFalse(registration_id_exists('321'))

            query_method.assert_called_with(
                DEFAULT_REGISTRATIONS_TABLE,
                filters={'id': '321'}
            )

    def test_lookup_subscription_id(self):
        filters = {'account_id': '12345', 'id': '55555'}

        with patch.object(Interactions, 'query', return_value=None) as \
                query_method:

            lookup_subscription_id('12345', '55555')

            query_method.assert_called_with(
                DEFAULT_SUBSCRIPTIONS_TABLE,
                filters=filters
            )

    def test_lookup_registration_id(self):
        filters = {'account_id': '4545', 'id': '5353'}

        with patch.object(Interactions, 'query', return_value=None) as \
                query_method:

            lookup_registration_id('4545', '5353')

            query_method.assert_called_with(
                DEFAULT_REGISTRATIONS_TABLE,
                filters=filters
            )

    def test_lookup_account_id(self):
        return_value = [
            {
                'id': '123'
            }
        ]

        filters = {'username': 'johndoe'}

        with patch.object(Interactions, 'query',
                          return_value=return_value) as query_method:

            ret = lookup_account_id('johndoe')

            self.assertEqual(ret, '123')

            query_method.assert_called_with(
                DEFAULT_ACCOUNTS_TABLE,
                filters=filters
            )
