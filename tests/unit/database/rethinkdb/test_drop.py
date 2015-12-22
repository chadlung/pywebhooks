# Standard lib imports
import unittest
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
import rethinkdb as rethink

# Project level imports
from pywebhooks import DEFAULT_DB_NAME
from pywebhooks.database.rethinkdb.drop import drop_database
from rethinkdb.errors import RqlRuntimeError, RqlDriverError


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingDrop())
    return test_suite


class WhenTestingDrop(unittest.TestCase):

    def setUp(self):
        pass

    @patch('pywebhooks.database.rethinkdb.drop.get_connection')
    def test_drop_database(self, connection_method):
        connection_method.return_value = Mock(__enter__=Mock, __exit__=Mock())

        with patch.object(rethink, 'db_drop', return_value=Mock()) as \
                db_drop_method:

            drop_database()

            db_drop_method.assert_called_once_with(DEFAULT_DB_NAME)

    @patch('pywebhooks.database.rethinkdb.drop.get_connection',
           side_effect=RqlDriverError(None))
    def test_drop_database_throws_rql_driver_error(self, _):
        with self.assertRaises(RqlDriverError) as cm:
            drop_database()
            self.assertEqual(cm.exception, RqlDriverError(None))

    @patch('pywebhooks.database.rethinkdb.drop.get_connection',
           side_effect=RqlRuntimeError(None, None, None))
    def test_drop_database_throws_rql_runtime_error(self, _):
        with self.assertRaises(RqlRuntimeError) as cm:
            drop_database()
            self.assertEqual(cm.exception, RqlRuntimeError(None, None, None))
