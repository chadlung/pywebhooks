from pywebhooks.util.request import http_request
from pywebhooks.util.request import HTTP_VERBS

from mock import MagicMock
from mock import patch

from httpretty import HTTPretty
from httpretty import httprettified

import requests
import unittest


def suite():
    suite = unittest.TestSuite()
    suite.addTest(WhenTestingUtilsRequest())
    return suite


class WhenTestingUtilsRequest(unittest.TestCase):

    def setUp(self):
        self.requests = MagicMock()
        self.url = 'http://localhost:8080/somewhere'
        self.json_payload = u'{}'


    @httprettified
    def test_should_raise_value_error(self):
        HTTPretty.register_uri(HTTPretty.PATCH, self.url,
                               body=self.json_payload,
                               content_type="application/json")

        with self.assertRaises(ValueError):
            http_request(self.url, json_payload=self.json_payload,
                         http_verb='PATCH')

    @httprettified
    def test_should_return_http_200_on_all_http_verbs(self):
        httpretty_verbs = {
            'POST': HTTPretty.POST,
            'GET': HTTPretty.GET,
            'DELETE': HTTPretty.DELETE,
            'PUT': HTTPretty.PUT,
            'HEAD': HTTPretty.HEAD,
        }

        for http_verb in HTTP_VERBS:
            HTTPretty.register_uri(httpretty_verbs[http_verb],
                                   self.url,
                                   body=self.json_payload,
                                   content_type="application/json",
                                   status=200)
            self.assertTrue(http_request(self.url,
                                         json_payload=self.json_payload,
                                         http_verb=http_verb), 200)

    def test_should_cause_a_connection_exception(self):
        with patch.object(requests, 'get') as mock_method:
            with self.assertRaises(requests.ConnectionError):
                mock_method.side_effect = requests.ConnectionError
                http_request(self.url, json_payload=self.json_payload)

    def test_should_cause_a_http_exception(self):
        with patch.object(requests, 'get') as mock_method:
            with self.assertRaises(requests.HTTPError):
                mock_method.side_effect = requests.HTTPError
                http_request(self.url, json_payload=self.json_payload)

    def test_should_cause_a_request_exception(self):
        with patch.object(requests, 'get') as mock_method:
            with self.assertRaises(requests.RequestException):
                mock_method.side_effect = requests.RequestException
                http_request(self.url, json_payload=self.json_payload)

if __name__ == '__main__':
    unittest.main()
