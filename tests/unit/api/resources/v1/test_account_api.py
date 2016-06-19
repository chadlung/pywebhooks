# Standard lib imports
from http import client
import unittest
from unittest.mock import patch

# Third party imports
# None

# Project level imports
from pywebhooks.app import app
from pywebhooks.api.resources.v1.account import account_api
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.api.decorators import authorization


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingAccountAPI())
    return test_suite


class WhenTestingAccountAPI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.test_headers = [
            ('api-key', '12345'),
            ('username', 'johndoe')
        ]
        self.client = app.test_client()

    def test_get_should_return_unsupported_media_type(self):
        resp = self.client.get('/v1/account/')
        self.assertEqual(resp.status_code, client.UNSUPPORTED_MEDIA_TYPE)

    def test_get_should_return_bad_request(self):
        resp = self.client.get('/v1/account/', content_type='application/json')
        self.assertEqual(resp.status_code, client.BAD_REQUEST)

    def test_get_should_return_unauthorized(self):
        with patch.object(Interactions, 'query', return_value=False):
            resp = self.client.get(
                '/v1/account/45712a61-a1b3-41a4-aa89-9593b909ae3d',
                content_type='application/json',
                headers=self.test_headers
            )
            self.assertEqual(resp.status_code, client.UNAUTHORIZED)

    def test_get_should_return_authorized(self):
        account_id = '45712a61-a1b3-41a4-aa89-9593b909ae3d'
        record = [
                {
                    'api_key': '12345'
                }
            ]

        with patch.object(authorization, 'check_password_hash',
                          return_value=True):
            with patch.object(account_api, 'lookup_account_id',
                              return_value=account_id):
                with patch.object(Interactions, 'query', return_value=record):
                    with patch.object(account_api, 'query', return_value={}):
                        resp = self.client.get(
                            '/v1/account/{0}'.format(account_id),
                            content_type='application/json',
                            headers=self.test_headers
                        )
                        self.assertEqual(resp.status_code, client.OK)
