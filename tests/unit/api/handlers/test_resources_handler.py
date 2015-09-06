# Standard lib imports
from http import client
import unittest
from unittest.mock import patch

# Third party imports
# None

# Project level imports
from pywebhooks.app import create_wsgi_app
from pywebhooks import DEFAULT_REGISTRATIONS_TABLE, \
    DEFAULT_SUBSCRIPTIONS_TABLE, DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.api.handlers.resources_handler import \
    registration_id_exists, lookup_subscription_id, lookup_registration_id, \
    lookup_account_id, validate_access


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingResourcesHandler())
    return test_suite


class WhenTestingResourcesHandler(unittest.TestCase):

    def setUp(self):
        self.app = create_wsgi_app()
        self.app.config['TESTING'] = True

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

    def test_validate_access_admin(self):
        self.assertIsNone(validate_access('admin'))

    @patch('pywebhooks.api.handlers.resources_handler.lookup_account_id')
    @patch('pywebhooks.api.handlers.resources_handler.lookup_registration_id')
    def test_validate_access_registration_id(self,
                                             lookup_registration_id_method,
                                             lookup_account_id_method,):
        with self.app.test_request_context():
            account_id = '555'
            registration_id = '444'

            lookup_account_id_method.return_value = account_id
            lookup_registration_id_method.return_value = True
            return_value = validate_access('fred', registration_id='444')

            self.assertIsNone(return_value)
            lookup_account_id_method.assert_called_with('fred')
            lookup_registration_id_method.assert_called_with(
                account_id, registration_id)
            lookup_registration_id_method.return_value = False
            response = validate_access('fred', registration_id='444')

            self.assertEqual(response.status_code, client.UNAUTHORIZED)

    @patch('pywebhooks.api.handlers.resources_handler.lookup_account_id')
    @patch('pywebhooks.api.handlers.resources_handler.lookup_subscription_id')
    def test_validate_access_subscription_id(self,
                                             lookup_subscription_id_method,
                                             lookup_account_id_method,):
        with self.app.test_request_context():
            account_id = '123'
            subscription_id = '775'

            lookup_account_id_method.return_value = account_id
            lookup_subscription_id_method.return_value = True
            return_value = validate_access('fred', subscription_id='775')

            self.assertIsNone(return_value)
            lookup_account_id_method.assert_called_with('fred')

            lookup_subscription_id_method.assert_called_with(
                account_id, subscription_id)
            lookup_subscription_id_method.return_value = False
            response = validate_access('fred', subscription_id='775')

            self.assertEqual(response.status_code, client.UNAUTHORIZED)

    @patch('pywebhooks.api.handlers.resources_handler.lookup_account_id')
    def test_validate_access_incoming_account_id(self,
                                                 lookup_account_id_method):

        with self.app.test_request_context():
            account_id = '111222'
            lookup_account_id_method.return_value = account_id

            response = validate_access(
                'fred', incoming_account_id='333444')

            lookup_account_id_method.assert_called_with('fred')
            self.assertEqual(response.status_code, client.UNAUTHORIZED)

            response = validate_access(
                'fred', incoming_account_id='111222')
            self.assertIsNone(response)
