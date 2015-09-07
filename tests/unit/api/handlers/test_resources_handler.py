# Standard lib imports
from http import client
import unittest
from unittest.mock import patch

# Third party imports
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
import requests_mock

# Project level imports
from pywebhooks.app import create_wsgi_app
from pywebhooks import DEFAULT_REGISTRATIONS_TABLE, \
    DEFAULT_SUBSCRIPTIONS_TABLE, DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.api.handlers.resources_handler import \
    registration_id_exists, lookup_subscription_id, lookup_registration_id, \
    lookup_account_id, validate_access, update, query, delete_all, \
    delete_accounts_except_admins, delete_registration, delete, insert, \
    insert_account, delete_account, client_reset_key, client_echo_valid, \
    reset_key


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WhenTestingResourcesHandler())
    return test_suite


class WhenTestingResourcesHandler(unittest.TestCase):

    def setUp(self):
        self.app = create_wsgi_app()
        self.app.config['TESTING'] = True

        self.param_kwargs = {
            'username': 'johndoe',
            'api_key': '123456789abcdef'
        }

    def test_registration_id_exists(self):
        with patch.object(Interactions, 'query', return_value=True) as \
                query_method:

            self.assertTrue(registration_id_exists('123'))

            query_method.assert_called_with(
                DEFAULT_REGISTRATIONS_TABLE,
                filters={'id': '123'}
            )

        with patch.object(Interactions, 'query', return_value=False) as \
                query_method:

            self.assertFalse(registration_id_exists('321'))

            query_method.assert_called_with(
                DEFAULT_REGISTRATIONS_TABLE,
                filters={'id': '321'}
            )

    def test_lookup_subscription_id(self):
        filters = {'account_id': '12345', 'id': '55555'}

        with patch.object(Interactions, 'query', return_value=None) as \
                query_method:

            lookup_subscription_id('12345', '55555')

            query_method.assert_called_with(
                DEFAULT_SUBSCRIPTIONS_TABLE,
                filters=filters
            )

    def test_lookup_registration_id(self):
        filters = {'account_id': '4545', 'id': '5353'}

        with patch.object(Interactions, 'query', return_value=None) as \
                query_method:

            lookup_registration_id('4545', '5353')

            query_method.assert_called_with(
                DEFAULT_REGISTRATIONS_TABLE,
                filters=filters
            )

    def test_lookup_account_id(self):
        return_value = [
            {
                'id': '123'
            }
        ]

        filters = {'username': 'johndoe'}

        with patch.object(Interactions, 'query',
                          return_value=return_value) as query_method:

            ret = lookup_account_id('johndoe')

            self.assertEqual(ret, '123')

            query_method.assert_called_with(
                DEFAULT_ACCOUNTS_TABLE,
                filters=filters
            )

    def test_validate_access_admin(self):
        self.assertIsNone(validate_access('admin'))

    @patch('pywebhooks.api.handlers.resources_handler.lookup_account_id')
    @patch('pywebhooks.api.handlers.resources_handler.lookup_registration_id')
    def test_validate_access_registration_id(self,
                                             lookup_registration_id_method,
                                             lookup_account_id_method,):
        with self.app.test_request_context():
            account_id = '555'
            registration_id = '444'

            lookup_account_id_method.return_value = account_id
            lookup_registration_id_method.return_value = True
            return_value = validate_access('fred', registration_id='444')

            self.assertIsNone(return_value)
            lookup_account_id_method.assert_called_with('fred')
            lookup_registration_id_method.assert_called_with(
                account_id, registration_id)
            lookup_registration_id_method.return_value = False
            response = validate_access('fred', registration_id='444')

            self.assertEqual(response.status_code, client.UNAUTHORIZED)

    @patch('pywebhooks.api.handlers.resources_handler.lookup_account_id')
    @patch('pywebhooks.api.handlers.resources_handler.lookup_subscription_id')
    def test_validate_access_subscription_id(self,
                                             lookup_subscription_id_method,
                                             lookup_account_id_method,):
        with self.app.test_request_context():
            account_id = '123'
            subscription_id = '775'

            lookup_account_id_method.return_value = account_id
            lookup_subscription_id_method.return_value = True
            return_value = validate_access('fred', subscription_id='775')

            self.assertIsNone(return_value)
            lookup_account_id_method.assert_called_with('fred')

            lookup_subscription_id_method.assert_called_with(
                account_id, subscription_id)
            lookup_subscription_id_method.return_value = False
            response = validate_access('fred', subscription_id='775')

            self.assertEqual(response.status_code, client.UNAUTHORIZED)

    @patch('pywebhooks.api.handlers.resources_handler.lookup_account_id')
    def test_validate_access_incoming_account_id(self,
                                                 lookup_account_id_method):

        with self.app.test_request_context():
            account_id = '111222'
            lookup_account_id_method.return_value = account_id

            response = validate_access(
                'fred', incoming_account_id='333444')

            lookup_account_id_method.assert_called_with('fred')
            self.assertEqual(response.status_code, client.UNAUTHORIZED)

            response = validate_access(
                'fred', incoming_account_id='111222')
            self.assertIsNone(response)

    def test_update_bad_request(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'update', return_value=None):
                response = update(DEFAULT_REGISTRATIONS_TABLE,
                                  record_id='123',
                                  username=None,
                                  updates={})
                self.assertEqual(response.status_code, client.BAD_REQUEST)

    def test_update_record_id(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'update', return_value={}):
                response = update(DEFAULT_REGISTRATIONS_TABLE,
                                  record_id='123',
                                  username=None,
                                  updates={})
                self.assertEqual(response.status_code, client.OK)

    def test_update_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'update',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = update(DEFAULT_REGISTRATIONS_TABLE,
                                  record_id='123', username=None, updates={})
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_update_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'update',
                              side_effect=RqlDriverError(None)):
                update(DEFAULT_REGISTRATIONS_TABLE,
                       record_id='123',
                       username=None,
                       updates={})
                self.assertRaises(RqlDriverError)

    def test_update_no_record_id(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'update', return_value={}):
                response = update(DEFAULT_REGISTRATIONS_TABLE,
                                  record_id=None,
                                  username='johndoe',
                                  updates={})
                self.assertEqual(response.status_code, client.OK)

    def test_query(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'get', return_value={}):
                response = query(DEFAULT_REGISTRATIONS_TABLE, record_id='123')
                self.assertEqual(response.status_code, client.OK)

    def test_query_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'get',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = query(DEFAULT_REGISTRATIONS_TABLE, record_id='123')
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_query_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'get',
                              side_effect=RqlDriverError(None)):
                response = query(DEFAULT_REGISTRATIONS_TABLE, record_id='123')
                self.assertRaises(RqlDriverError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_all(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_all', return_value={}):
                response = delete_all(DEFAULT_REGISTRATIONS_TABLE)
                self.assertEqual(response.status_code, client.OK)

    def test_delete_all_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_all',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = delete_all(DEFAULT_REGISTRATIONS_TABLE)
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_all_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_all',
                              side_effect=RqlDriverError(None)):
                response = delete_all(DEFAULT_REGISTRATIONS_TABLE)
                self.assertRaises(RqlDriverError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_accounts_except_admins(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_specific',
                              return_value={}):
                response = delete_accounts_except_admins()
                self.assertEqual(response.status_code, client.OK)

    def test_delete_accounts_except_admins_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_specific',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = delete_accounts_except_admins()
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_accounts_except_admins_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_specific',
                              side_effect=RqlDriverError(None)):
                response = delete_accounts_except_admins()
                self.assertRaises(RqlDriverError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_registration(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_specific',
                              return_value={}):
                response = delete_registration('123')
                self.assertEqual(response.status_code, client.OK)

    def test_delete_registration_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_specific',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = delete_registration('123')
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_registration_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_specific',
                              side_effect=RqlDriverError(None)):
                response = delete_registration('123')
                self.assertRaises(RqlDriverError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_registration_type_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_specific',
                              side_effect=TypeError):
                response = delete_registration('123')
                self.assertRaises(TypeError)
                self.assertEqual(response.status_code,
                                 client.BAD_REQUEST)

    def test_delete(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete',
                              return_value={}):
                response = delete(DEFAULT_SUBSCRIPTIONS_TABLE, '123')
                self.assertEqual(response.status_code, client.OK)

    def test_delete_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = delete(DEFAULT_SUBSCRIPTIONS_TABLE, '123')
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete',
                              side_effect=RqlDriverError(None)):
                response = delete(DEFAULT_SUBSCRIPTIONS_TABLE, '123')
                self.assertRaises(RqlDriverError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_type_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'delete',
                              side_effect=TypeError):
                response = delete(DEFAULT_SUBSCRIPTIONS_TABLE, '123')
                self.assertRaises(TypeError)
                self.assertEqual(response.status_code,
                                 client.BAD_REQUEST)

    def test_insert(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'insert',
                              return_value={}):
                response = insert(DEFAULT_SUBSCRIPTIONS_TABLE,
                                  **self.param_kwargs)
                self.assertEqual(response.status_code, client.CREATED)

    def test_insert_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'insert',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = insert(DEFAULT_SUBSCRIPTIONS_TABLE,
                                  **self.param_kwargs)
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_insert_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'insert',
                              side_effect=RqlDriverError(None)):
                response = insert(DEFAULT_SUBSCRIPTIONS_TABLE,
                                  **self.param_kwargs)
                self.assertRaises(RqlDriverError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_insert_type_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'insert',
                              side_effect=TypeError):
                response = insert(DEFAULT_SUBSCRIPTIONS_TABLE,
                                  **self.param_kwargs)
                self.assertRaises(TypeError)
                self.assertEqual(response.status_code,
                                 client.BAD_REQUEST)

    def test_insert_account(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              return_value={}):
                with patch.object(Interactions, 'insert',
                                  return_value={'id': '123'}):
                    response = insert_account(DEFAULT_SUBSCRIPTIONS_TABLE,
                                              **self.param_kwargs)
                    self.assertEqual(response.status_code, client.CREATED)

    def test_insert_account_conflict(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              return_value={'username': 'johndoe'}):
                response = insert_account(DEFAULT_SUBSCRIPTIONS_TABLE,
                                          **self.param_kwargs)
                self.assertEqual(response.status_code, client.CONFLICT)

    def test_insert_account_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = insert_account(DEFAULT_SUBSCRIPTIONS_TABLE,
                                          **self.param_kwargs)
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_insert_account_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              side_effect=RqlDriverError(None)):
                response = insert_account(DEFAULT_SUBSCRIPTIONS_TABLE,
                                          **self.param_kwargs)
                self.assertRaises(RqlDriverError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_insert_account_type_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              side_effect=TypeError):
                response = insert_account(DEFAULT_SUBSCRIPTIONS_TABLE,
                                          **self.param_kwargs)
                self.assertRaises(TypeError)
                self.assertEqual(response.status_code,
                                 client.BAD_REQUEST)

    @patch('pywebhooks.api.handlers.resources_handler.delete_registration')
    def test_delete_account(self, delete_registration_method):
        delete_registration_method.return_value = None

        with self.app.test_request_context():
            with patch.object(Interactions, 'delete_specific',
                              return_value=[{'id': '123'}]):
                with patch.object(Interactions, 'query',
                                  return_value={}):
                    with patch.object(Interactions, 'delete',
                                      return_value={}):
                        response = delete_account('123')
                        self.assertEqual(response.status_code, client.OK)

    def test_delete_account_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              side_effect=RqlRuntimeError(None, None, None)):
                response = insert_account(DEFAULT_SUBSCRIPTIONS_TABLE,
                                          **self.param_kwargs)
                self.assertRaises(RqlRuntimeError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_account_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              side_effect=RqlDriverError(None)):
                response = insert_account(DEFAULT_SUBSCRIPTIONS_TABLE,
                                          **self.param_kwargs)
                self.assertRaises(RqlDriverError)
                self.assertEqual(response.status_code,
                                 client.INTERNAL_SERVER_ERROR)

    def test_delete_account_type_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              side_effect=TypeError):
                response = insert_account(DEFAULT_SUBSCRIPTIONS_TABLE,
                                          **self.param_kwargs)
                self.assertRaises(TypeError)
                self.assertEqual(response.status_code,
                                 client.BAD_REQUEST)

    def test_client_reset_key_success(self):
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('GET', 'http://localhost/endpoint',
                                json={'api_key': '54321'},
                                status_code=client.OK)

            return_value = client_reset_key('http://localhost/endpoint',
                                            'api_key', '12345')

            self.assertTrue(return_value)

    def test_client_reset_key_fail(self):
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('GET', 'http://localhost/endpoint/hello',
                                json={'api_key': '54321'},
                                status_code=client.OK)

            return_value = client_reset_key('http://localhost/endpoint',
                                            'api_key', '12345')

            self.assertFalse(return_value)

    @patch('pywebhooks.utils.common.generate_key')
    def test_client_echo_valid_success(self, generate_key_method):
        generate_key_method.return_value = '12345GENKEY'

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('GET', 'http://localhost/endpoint',
                                json={'echo': '12345GENKEY'},
                                status_code=client.OK)

            self.assertTrue(client_echo_valid('http://localhost/endpoint'))

    def test_client_echo_valid_fail_wrong_key(self):
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('GET', 'http://localhost/endpoint',
                                json={'echo': '12345GENKEY'},
                                status_code=client.OK)

            self.assertFalse(client_echo_valid('http://localhost/endpoint'))

    def test_client_echo_valid_fail_wrong_status(self):
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('GET', 'http://localhost/endpoint',
                                json={'echo': '12345GENKEY'},
                                status_code=client.INTERNAL_SERVER_ERROR)

            self.assertFalse(client_echo_valid('http://localhost/endpoint'))

    def test_reset_key_endpoint_not_found(self):
        records = [{'endpoint': ''}]

        with self.app.test_request_context():
            with patch.object(Interactions, 'query', return_value=records):
                response = reset_key('johndoe', 'api_key')
                self.assertEqual(response.status_code,
                                 client.NOT_FOUND)

    def test_reset_key_endpoint_call_fail(self):
        records = [{'endpoint': 'http://localhost/endpoint'}]

        with self.app.test_request_context():
            with patch.object(Interactions, 'query', return_value=records):
                response = reset_key('johndoe', 'api_key')
                self.assertEqual(response.status_code,
                                 client.BAD_REQUEST)

    @patch('pywebhooks.api.handlers.resources_handler.client_reset_key')
    def test_reset_key_api_key(self, client_reset_key_method):
        records = [{'endpoint': 'http://localhost/endpoint'}]
        client_reset_key_method.return_value = True

        with self.app.test_request_context():
            with patch.object(Interactions, 'query', return_value=records):
                with patch.object(Interactions, 'update', return_value=None):
                    response = reset_key('johndoe', 'api_key')
                    self.assertEqual(response.status_code, client.OK)

    @patch('pywebhooks.api.handlers.resources_handler.client_reset_key')
    def test_reset_key_secret_key(self, client_reset_key_method):
        records = [{'endpoint': 'http://localhost/endpoint'}]
        client_reset_key_method.return_value = True

        with self.app.test_request_context():
            with patch.object(Interactions, 'query', return_value=records):
                with patch.object(Interactions, 'update', return_value=None):
                    response = reset_key('johndoe', 'secret_key')
                    self.assertEqual(response.status_code, client.OK)

    def test_reset_key_rql_runtime_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              side_effect=RqlRuntimeError(None, None, None)):
                    response = reset_key('johndoe', 'api_key')
                    self.assertRaises(RqlRuntimeError)
                    self.assertEqual(response.status_code,
                                     client.INTERNAL_SERVER_ERROR)

    def test_reset_key_rql_driver_error(self):
        with self.app.test_request_context():
            with patch.object(Interactions, 'query',
                              side_effect=RqlDriverError(None)):
                    response = reset_key('johndoe', 'api_key')
                    self.assertRaises(RqlDriverError)
                    self.assertEqual(response.status_code,
                                     client.INTERNAL_SERVER_ERROR)
