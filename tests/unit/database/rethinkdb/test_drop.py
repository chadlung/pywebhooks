# Standard lib imports
import unittest
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
import rethinkdb as rethink

# Project level imports
from pywebhooks import DEFAULT_DB_NAME
from pywebhooks.database.rethinkdb.drop import drop_database


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

            db_drop_method.assert_called_once()
            db_drop_method.run.assert_called_once()
            db_drop_method.assert_called_with(DEFAULT_DB_NAME)
