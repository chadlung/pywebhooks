# Standard lib imports
from http import client
import unittest
from unittest.mock import patch

# Third party imports
# None

# Project level imports
from pywebhooks.app import create_wsgi_app
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.api.decorators.validation import validate_id_params,\
    validate_username_in_header, validate_pagination_params
from pywebhooks.database.rethinkdb.interactions import Interactions


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingValidation())
    return test_suite


class WhenTestingValidation(unittest.TestCase):

    def setUp(self):
        self.app = create_wsgi_app()
        self.app.config['TESTING'] = True

    def test_validate_id_params_bad_request(self):

        @validate_id_params(None)
        def test_func():
            pass

        with self.app.test_request_context():
            response = test_func()
            self.assertEqual(response.status_code, client.BAD_REQUEST)

    def test_validate_username_in_header_bad_request(self):

        @validate_username_in_header()
        def test_func():
            pass

        with self.app.test_request_context():
            response = test_func()
            self.assertEqual(response.status_code, client.BAD_REQUEST)

    def test_validate_username_in_header_not_found(self):
        with patch.object(Interactions, 'query', return_value=False):
            @validate_username_in_header()
            def test_func():
                pass

            test_header = [('username', 'johndoe')]

            with self.app.test_request_context(headers=test_header):
                response = test_func()
                self.assertEqual(response.status_code, client.NOT_FOUND)

    def test_validate_username_in_header(self):
        with patch.object(Interactions, 'query', return_value=True) as \
                query_method:
            @validate_username_in_header()
            def test_func():
                pass

            test_header = [('username', 'johndoe')]

            with self.app.test_request_context(headers=test_header):
                test_func()
                query_method.assert_called_with(
                    DEFAULT_ACCOUNTS_TABLE,
                    filters={'username': 'johndoe'}
                )

    def test_validate_pagination_params_invalid_start(self):
            @validate_pagination_params()
            def test_func():
                pass

            with self.app.test_request_context('/?limit=10&start=-1'):
                response = test_func()
                self.assertEqual(response.status_code, client.BAD_REQUEST)

            with self.app.test_request_context('/?limit=10'
                                               '&start=9999999999999991'):
                response = test_func()
                self.assertEqual(response.status_code, client.BAD_REQUEST)

    def test_validate_pagination_params_invalid_limit(self):
        @validate_pagination_params()
        def test_func():
            pass

        with self.app.test_request_context('/?limit=-1&start=0'):
            response = test_func()
            self.assertEqual(response.status_code, client.BAD_REQUEST)

        with self.app.test_request_context('/?limit=101&start=0'):
            response = test_func()
            self.assertEqual(response.status_code, client.BAD_REQUEST)

    def test_validate_pagination_params(self):
        @validate_pagination_params()
        def test_func():
            pass

        with self.app.test_request_context('/?limit=1&start=0'):
            self.assertIsNone(test_func())
