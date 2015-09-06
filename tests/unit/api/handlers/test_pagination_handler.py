# Standard lib imports
from http import client
import unittest
from unittest.mock import patch

# Third party imports
from flask import request

# Project level imports
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.api.handlers.pagination_handler import paginate
from pywebhooks.app import create_wsgi_app
from pywebhooks.database.rethinkdb.interactions import Interactions


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingpaginationHanlder())
    return test_suite


class WhenTestingpaginationHanlder(unittest.TestCase):

    def setUp(self):
        self.app = create_wsgi_app()
        self.app.config['TESTING'] = True

        self.returned_records = \
            [{'description': 'jane doe registered webhook',
              'event_data': {'message': 'Jane Doe'},
              'epoch': 1441563242.268688,
              'account_id': '04ee97a8-2f77-4117-bc96-fe8a33497c36',
              'id': '069bce36-b2bf-4771-96c5-468eb37665d5',
              'event': 'janedoe.event'},
             {'description': 'john doe registered webhook',
              'event_data': {'message': 'John Doe'},
              'epoch': 1441563242.300409,
              'account_id': 'd382e86c-913d-4a06-abdc-232b963a8f8f',
              'id': '047e549a-24a1-4194-8a41-c56b525cb815',
              'event': 'johndoe.event'},
             {
                 'description': 'leah richards registered webhook',
                 'event_data': {'message': 'Leah Richards'},
                 'epoch': 1441563242.331244,
                 'account_id': '45012169-902e-4d24-80ba-d2f2061baef3',
                 'id': '50e2148f-7b43-4b85-a524-4dc64fc521fc',
                 'event': 'leahrichards.event'}]

    def test_validate_pagination_params_no_content(self):
        with self.app.test_request_context('/?limit=10&start=0', method='GET'):
            with patch.object(Interactions, 'list', return_value=[]):
                response = paginate(
                    request, DEFAULT_ACCOUNTS_TABLE, 'accounts'
                )
                self.assertEqual(response.status_code, client.NO_CONTENT)

    def test_validate_pagination_params(self):
        with self.app.test_request_context('/?limit=10&start=0', method='GET'):
            with patch.object(Interactions, 'list',
                              return_value=self.returned_records):
                response = paginate(
                    request, DEFAULT_ACCOUNTS_TABLE, 'accounts', filters=None
                )
                self.assertEqual(response.status_code, client.OK)
                self.assertTrue('next_start' not in str(response.data))

    def test_validate_pagination_params_wth_next_marker(self):
        with self.app.test_request_context('/?limit=1&start=0', method='GET'):
            with patch.object(Interactions, 'list',
                              return_value=self.returned_records):
                response = paginate(
                    request, DEFAULT_ACCOUNTS_TABLE, 'accounts'
                )
                self.assertTrue('next_start' in str(response.data))
                self.assertEqual(response.status_code, client.OK)
