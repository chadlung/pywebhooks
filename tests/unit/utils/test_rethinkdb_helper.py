# Standard lib imports
import unittest
from unittest.mock import patch

# Third party imports
import rethinkdb as rethink

# Project level imports
from pywebhooks import DEFAULT_DB_NAME
from pywebhooks.utils.rethinkdb_helper import get_connection


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingRethinkDBHelper())
    return test_suite


class WhenTestingRethinkDBHelper(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_connection(self):
        with patch.object(rethink, 'connect', return_value=None) as \
                connect_method:

            get_connection()

            connect_method.assert_called_once()
            connect_method.assert_called_with(host='localhost', port=28015,
                                              auth_key='', db=DEFAULT_DB_NAME)
