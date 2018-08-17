# Standard lib imports
from http import client
import unittest
from unittest.mock import patch

# Third party imports
# None

# Project level imports
from pywebhooks.app import create_wsgi_app
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.api.decorators.authorization import api_key_restricted_resource
from pywebhooks.database.rethinkdb.interactions import Interactions


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingAuthorization())
    return test_suite


class WhenTestingAuthorization(unittest.TestCase):

    def setUp(self):
        self.app = create_wsgi_app()
        self.app.config['TESTING'] = True
        self.test_headers = [('api-key', '12345'), ('username', 'johndoe')]

    def test_validate_id_params_unauthorized(self):
        with patch.object(Interactions, 'query', return_value=False) as \
                query_method:
            @api_key_restricted_resource(verify_admin=False)
            def test_func():
                pass

            missing_api_key_header = [('test', 'test')]

            with self.app.test_request_context(headers=missing_api_key_header):
                response = test_func()
                self.assertEqual(response.status_code, client.UNAUTHORIZED)

            missing_username_header = [('api-key', '12345')]

            with self.app.test_request_context(headers=missing_username_header):
                response = test_func()
                self.assertEqual(response.status_code, client.UNAUTHORIZED)

            with self.app.test_request_context(headers=self.test_headers):
                response = test_func()
                self.assertEqual(response.status_code, client.UNAUTHORIZED)

                query_method.assert_called_with(
                    DEFAULT_ACCOUNTS_TABLE,
                    filters={'username': 'johndoe'}
                )

    def test_validate_id_params_unauthorized_invalid_api_key(self):
        with patch.object(Interactions, 'query',
                          return_value=[{'api_key': '12345'}]):

            @api_key_restricted_resource(verify_admin=False)
            def test_func():
                pass

            with self.app.test_request_context(headers=self.test_headers):
                response = test_func()
                self.assertEqual(
                    response.data,
                    b'{"Error":"Invalid API key"}\n'
                )
                self.assertEqual(response.status_code, client.UNAUTHORIZED)
