# Standard lib imports
import hashlib
import hmac
import json
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
        self.json_data = "{'message': 'hello world'}"

        self.signature = hmac.new(
            str(self.secret_key).encode('utf-8'),
            str(json.dumps(self.json_data)).encode('utf-8'),
            digestmod=hashlib.sha1
        ).digest()

    def test_bad_secret_key(self):
        test_signature = hmac.new(
            str('bad-secret-key').encode('utf-8'),
            str(json.dumps(self.json_data)).encode('utf-8'),
            digestmod=hashlib.sha1
        ).hexdigest()

        self.assertNotEqual(
            test_signature,
            create_signature(self.secret_key, self.json_data)
        )

    def test_good_secret_key(self):
        test_signature = hmac.new(
            str(self.secret_key).encode('utf-8'),
            str(json.dumps(self.json_data)).encode('utf-8'),
            digestmod=hashlib.sha1
        ).hexdigest()

        self.assertEqual(
            test_signature,
            create_signature(self.secret_key, self.json_data)
        )

    def test_generate_key(self):
        self.assertTrue(generate_key())
        self.assertEqual(len(generate_key()), 40)
