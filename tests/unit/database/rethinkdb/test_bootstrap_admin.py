# Standard lib imports
import unittest
from unittest.mock import patch

# Third party imports
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

# Project level imports
from pywebhooks.database.rethinkdb.bootstrap_admin import create_admin_account
from pywebhooks.database.rethinkdb.interactions import Interactions


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingBootstrapAdminFunctions())
    return test_suite


class WhenTestingBootstrapAdminFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_admin_account(self):
        with patch.object(Interactions, 'insert', return_value=None) as \
                insert_method:

            return_data = create_admin_account()

            insert_method.assert_called_once()

            self.assertTrue('api_key' in return_data)
            self.assertTrue('secret_key' in return_data)

            self.assertEqual(len(return_data['api_key']), 40)
            self.assertEqual(len(return_data['secret_key']), 40)

    def test_create_admin_account_throws_rql_runtime_error(self):
        with patch.object(Interactions, 'insert',
                          side_effect=RqlRuntimeError(None, None, None)):

            create_admin_account()
            self.assertRaises(RqlRuntimeError)

    def test_create_admin_account_throws_rql_driver_error(self):
        with patch.object(Interactions, 'insert',
                          side_effect=RqlDriverError(None)):

            create_admin_account()
            self.assertRaises(RqlDriverError)
