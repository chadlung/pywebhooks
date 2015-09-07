# Standard lib imports
from http import client
import unittest

# Third party imports
import requests_mock

# Project level imports
from pywebhooks.utils.request_handler import RequestHandler


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingRequestHandler())
    return test_suite


class WhenTestingRequestHandler(unittest.TestCase):

    def setUp(self):
        pass

    def test_get(self):

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('GET', 'http://localhost?test=123',
                                json={'test': 'value'},
                                status_code=200)

            request_handler = RequestHandler()
            data, status = request_handler.get(
                'http://localhost',
                params={'test': 123},
                api_key='12345',
                username='johndoe'
            )
            self.assertEqual(status, client.OK)
            self.assertEqual({'test': 'value'}, data)
            self.assertEqual(request_handler.headers['username'], 'johndoe')
            self.assertEqual(request_handler.headers['api-key'], '12345')
            self.assertEqual(
                request_handler.headers['Content-Type'], 'application/json')
            self.assertEqual(
                request_handler.headers['Accept'], 'application/json')

    def test_put(self):

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('PUT', 'http://localhost',
                                json={'test': 'value'},
                                status_code=200)

            request_handler = RequestHandler()
            data, status = request_handler.put(
                'http://localhost',
                json_payload={'hello': 'world'},
                api_key='555',
                username='janedoe'
            )
            self.assertEqual(status, client.OK)
            self.assertEqual({'test': 'value'}, data)
            self.assertEqual(request_handler.headers['username'], 'janedoe')
            self.assertEqual(request_handler.headers['api-key'], '555')
            self.assertEqual(
                request_handler.headers['Content-Type'], 'application/json')
            self.assertEqual(
                request_handler.headers['Accept'], 'application/json')

    def test_post(self):

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', 'http://localhost',
                                json={'test': 'value'},
                                status_code=201)

            request_handler = RequestHandler()
            data, status = request_handler.post(
                'http://localhost',
                json_payload={'hello': 'world'},
                api_key='8900',
                username='samjones',
                event='myevent',
                signature='mysignature'
            )
            self.assertEqual(status, client.CREATED)
            self.assertEqual({'test': 'value'}, data)
            self.assertEqual(request_handler.headers['username'], 'samjones')
            self.assertEqual(request_handler.headers['api-key'], '8900')
            self.assertEqual(request_handler.headers['event'], 'myevent')
            self.assertEqual(
                request_handler.headers['pywebhooks-signature'], 'mysignature')
            self.assertEqual(
                request_handler.headers['Content-Type'], 'application/json')
            self.assertEqual(
                request_handler.headers['Accept'], 'application/json')

    def test_patch(self):

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('PATCH', 'http://localhost',
                                json={'test': 'value'},
                                status_code=200)

            request_handler = RequestHandler()
            data, status = request_handler.patch(
                'http://localhost',
                json_payload={'hello': 'world'},
                api_key='01245',
                username='natml'
            )
            self.assertEqual(status, client.OK)
            self.assertEqual({'test': 'value'}, data)
            self.assertEqual(request_handler.headers['username'], 'natml')
            self.assertEqual(request_handler.headers['api-key'], '01245')
            self.assertEqual(
                request_handler.headers['Content-Type'], 'application/json')
            self.assertEqual(
                request_handler.headers['Accept'], 'application/json')

    def test_delete(self):

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('DELETE', 'http://localhost/45678',
                                json={'test': 'value'},
                                status_code=200)

            request_handler = RequestHandler()
            data, status = request_handler.delete(
                'http://localhost/45678',
                api_key='765434',
                username='birk'
            )
            self.assertEqual(status, client.OK)
            self.assertEqual({'test': 'value'}, data)
            self.assertEqual(request_handler.headers['username'], 'birk')
            self.assertEqual(request_handler.headers['api-key'], '765434')
            self.assertEqual(
                request_handler.headers['Content-Type'], 'application/json')
            self.assertEqual(
                request_handler.headers['Accept'], 'application/json')
