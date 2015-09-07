# Standard lib imports
from http import client
import unittest
from unittest.mock import patch

# Third party imports
# None

# Project level imports
from pywebhooks.app import before_request, create_wsgi_app


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingAppFunctions())
    return test_suite


class WhenTestingAppFunctions(unittest.TestCase):

    def setUp(self):
        self.app = create_wsgi_app()
        self.app.config['TESTING'] = True

    @patch('pywebhooks.app.before_request')
    def test_before_request(self, before_request_decorator):
        before_request_decorator.return_value = None

        with self.app.test_request_context():
            msg, status = before_request()

            self.assertEqual(status, client.UNSUPPORTED_MEDIA_TYPE)
            self.assertEqual('Unsupported Media Type', msg)
