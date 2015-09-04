# Standard lib imports
import base64
import hashlib
import hmac
import unittest

# Third party imports
# None

# Project level imports
from pywebhooks.utils.common import create_signature, generate_key


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingCommonFunctions())
    return test_suite


class WhenTestingCommonFunctions(unittest.TestCase):

    def setUp(self):
        self.secret_key = 'secret-key'
        self.json_data = '{"hello": "world}'

        self.base64_encoded_signature = base64.urlsafe_b64encode(hmac.new(
            str(self.secret_key).encode('utf-8'),
            str(self.json_data).encode('utf-8'),
            digestmod=hashlib.sha1
        ).digest())

        self.signature = hmac.new(
            str(self.secret_key).encode('utf-8'),
            str(self.json_data).encode('utf-8'),
            digestmod=hashlib.sha1
        ).digest()

    def test_secret_key(self):
        test_signature = base64.urlsafe_b64encode(hmac.new(
            str('bad-secret-key').encode('utf-8'),
            str(self.json_data).encode('utf-8'),
            digestmod=hashlib.sha1
        ).digest())

        self.assertNotEqual(
            test_signature,
            create_signature(self.secret_key, self.json_data)
        )

    def test_base64_encoded_signature(self):
        self.assertEqual(
            self.base64_encoded_signature,
            create_signature(self.secret_key, self.json_data)
        )

    def test_no_base64_encoded_signature(self):
        self.assertEqual(
            self.signature,
            create_signature(
                self.secret_key, self.json_data, base64_encode=False
            )
        )

        self.assertNotEqual(
            self.signature,
            create_signature(
                self.secret_key, self.json_data, base64_encode=True
            )
        )

    def test_generate_key(self):
        self.assertTrue(generate_key())
        self.assertEqual(len(generate_key()), 40)
