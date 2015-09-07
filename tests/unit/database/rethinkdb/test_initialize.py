# Standard lib imports
import unittest
from unittest.mock import Mock
from unittest.mock import patch

# Third party imports
import rethinkdb as rethink

# Project level imports
from pywebhooks.database.rethinkdb.initialize import create_database


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingInitialize())
    return test_suite


class WhenTestingInitialize(unittest.TestCase):

    def setUp(self):
        pass

    @patch('pywebhooks.database.rethinkdb.drop.get_connection')
    def test_create_database(self, connection_method):
        connection_method.return_value = Mock(__enter__=Mock, __exit__=Mock())

        with patch.object(rethink, 'db_list') as db_list_method:
            db_list_method.return_value.run.return_value = ['rethinkdb']

            with patch.object(rethink, 'db_create') as db_create_method:
                db_create_method.return_value.run.return_value = None

                with patch.object(rethink, 'db') as db_method:
                    db_method.return_value.table_list.return_value. \
                        run.return_value = []

                    create_database()

                    db_list_method.assert_called_once()
                    db_create_method.assert_called_once()
                    db_method.assert_called_once()
