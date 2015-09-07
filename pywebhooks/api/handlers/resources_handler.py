# Standard lib imports
from http import client

# Third-party imports
from flask import make_response, jsonify
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from werkzeug.security import generate_password_hash

# Project-level imports
from pywebhooks import DEFAULT_SUBSCRIPTIONS_TABLE, \
    REQUEST_TIMEOUT, DEFAULT_ACCOUNTS_TABLE, DEFAULT_REGISTRATIONS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions
from pywebhooks.utils import common
from pywebhooks.utils.request_handler import RequestHandler


def insert_account(table_name, **kwargs):
    """
    Creates new account records (handles POST traffic)
    Salts the api_key
    """
    try:
        # Username cannot already exist
        record = Interactions.query(
            table_name, filters={'username': kwargs['username']})

        if record:
            return make_response(
                jsonify({'Error': 'Username already exists'}), client.CONFLICT)

        original_api_key = kwargs['api_key']
        kwargs['api_key'] = generate_password_hash(kwargs['api_key'])
        account_data = Interactions.insert(table_name, **kwargs)
        account_data['api_key'] = original_api_key

        return make_response(jsonify(account_data), client.CREATED)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except TypeError:
        return make_response(
            jsonify({'Error': 'Invalid parameter(s)'}), client.BAD_REQUEST)


def insert(table_name, **kwargs):
    """
    Creates new records (handles POST traffic)
    """
    try:
        return make_response(
            jsonify(Interactions.insert(table_name, **kwargs)), client.CREATED)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except TypeError:
        return make_response(
            jsonify({'Error': 'Invalid parameter(s)'}), client.BAD_REQUEST)


def delete(table_name, record_id):
    """
    Deletes a single record (handles DELETE traffic)
    """
    try:
        return make_response(
            jsonify(Interactions.delete(table_name, record_id)), client.OK)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except TypeError:
        return make_response(
            jsonify({'Error': 'Invalid id parameter'}), client.BAD_REQUEST)


def delete_account(record_id):
    """
    Deletes a single account record, removes all traces of account from other
    tables
    """
    try:
        # Delete this account's subscriptions
        Interactions.delete_specific(
            DEFAULT_SUBSCRIPTIONS_TABLE, filters={'account_id': record_id})

        # Loop and delete any records subscribed to their registrations
        registrations = Interactions.query(DEFAULT_REGISTRATIONS_TABLE,
                                           filters={'account_id': record_id})

        for registration in registrations:
            delete_registration(registration['id'])

        return make_response(
            jsonify(Interactions.delete(DEFAULT_ACCOUNTS_TABLE, record_id)),
            client.OK)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except TypeError:
        return make_response(
            jsonify({'Error': 'Invalid id parameter'}), client.BAD_REQUEST)


def delete_registration(registration_id):
    """
    Deletes a single registration record, removes all traces of this
    registration from the subscription table
    """
    try:
        Interactions.delete_specific(
            DEFAULT_SUBSCRIPTIONS_TABLE,
            filters={'registration_id': registration_id})

        return make_response(
            jsonify(Interactions.delete_specific(
                DEFAULT_REGISTRATIONS_TABLE,
                filters={'id': registration_id})), client.OK)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except TypeError:
        return make_response(
            jsonify({'Error': 'Invalid id parameter'}), client.BAD_REQUEST)


def delete_accounts_except_admins():
    """
    Deletes all account records except those marked as admins, removes all
    traces of account from other tables
    """
    try:
        return make_response(
            jsonify(Interactions.delete_specific(
                DEFAULT_ACCOUNTS_TABLE,
                filters={'is_admin': False})), client.OK)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)


def delete_all(table_name):
    """
    Deletes all records (handles DELETE traffic)
    """
    try:
        return make_response(
            jsonify(Interactions.delete_all(table_name)), client.OK)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)


def query(table_name, record_id):
    """
    Gets a single record (handles GET traffic)
    """
    try:
        return make_response(
            jsonify(Interactions.get(table_name, record_id)), client.OK)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except TypeError:
        return make_response(
            jsonify({'Error': 'Invalid id parameter'}), client.BAD_REQUEST)


def update(table_name, record_id=None, username=None, updates={}):
    """
    Updates a single record (handles GET traffic)
    """
    try:
        if record_id:
            return make_response(
                jsonify(Interactions.update(
                    table_name, record_id=record_id, updates=updates)),
                client.OK)
        else:
            return make_response(
                jsonify(Interactions.update(
                    table_name,
                    filters={'username': username},
                    updates=updates)
                ), client.OK)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except TypeError:
        return make_response(
            jsonify({'Error': 'Invalid parameter(s)'}), client.BAD_REQUEST)


def client_echo_valid(endpoint):
    """
    This will validate if the user's endpoint is valid and returning the echo
    data sent to it
    """
    try:
        request_handler = RequestHandler(
            verify_ssl=False, request_timeout=REQUEST_TIMEOUT)
        validation_key = common.generate_key()

        try:
            returned_json, status_code = request_handler.get(
                endpoint, params={'echo': validation_key})
        # pylint: disable=W0703
        except:
            return False

        if status_code != client.OK:
            return False
        if returned_json['echo'] != validation_key:
            return False
    # pylint: disable=W0703
    except Exception:
        return False

    return True


def client_reset_key(endpoint, key_type, key_value):
    """
    This will send an api_key or secret_key to the configured endpoint
    (assists with resets of an api_key or secret_key)
    """
    try:
        request_handler = RequestHandler(
            verify_ssl=False, request_timeout=REQUEST_TIMEOUT)

        try:
            returned_json, status_code = request_handler.get(
                endpoint, params={key_type: key_value})
        # pylint: disable=W0703
        except:
            return False

        if status_code != client.OK:
            return False
    # pylint: disable=W0703
    except Exception:
        return False

    return True


def reset_key(username, key_type):
    """
    Resets either a secret key or api key
    """
    try:
        # Note: The validate_username_in_header decorator will verify the
        # username and record. The api_key_restricted_resource will validate
        # the username as well as a valid API key
        record = Interactions.query(DEFAULT_ACCOUNTS_TABLE,
                                    filters={"username": username})
        endpoint = record[0]['endpoint']

        if not endpoint:
            return make_response(
                jsonify({'Error': 'Endpoint not found'}),
                client.NOT_FOUND
            )

        new_key = common.generate_key()
        salted_new_key = generate_password_hash(new_key)

        if not client_reset_key(endpoint, key_type, new_key):
            return make_response(
                jsonify({'Error': 'Failed to contact the endpoint or wrong '
                                  'HTTP status code returned'}),
                client.BAD_REQUEST
            )

        if key_type == 'api_key':
            update = {key_type: salted_new_key}
        else:
            update = {key_type: new_key}

        Interactions.update(DEFAULT_ACCOUNTS_TABLE,
                            filters={"username": username},
                            updates=update)

        return make_response(jsonify({'Message': 'New key sent to endpoint'}),
                             client.OK)
    except RqlRuntimeError as runtime_err:
        return make_response(jsonify({'Error': runtime_err.message}),
                             client.INTERNAL_SERVER_ERROR)
    except RqlDriverError as rql_err:
        return make_response(jsonify({'Error': rql_err.message}),
                             client.INTERNAL_SERVER_ERROR)


def lookup_account_id(username):
    """
    Looks up the user's account id based on username
    """
    try:
        record = Interactions.query(
            DEFAULT_ACCOUNTS_TABLE, filters={'username': username})
        return record[0]['id']
    except RqlRuntimeError as runtime_err:
        return runtime_err
    except RqlDriverError as rql_err:
        return rql_err


def lookup_registration_id(account_id, registration_id):
    """
    Looks up registration based on account_id and pass the record back
    """
    try:
        return Interactions.query(
            DEFAULT_REGISTRATIONS_TABLE,
            filters={'account_id': account_id, 'id': registration_id})
    except RqlRuntimeError as runtime_err:
        return runtime_err
    except RqlDriverError as rql_err:
        return rql_err


def lookup_subscription_id(account_id, subscription_id):
    """
    Looks up subscription based on account_id and pass the record back
    """
    try:
        return Interactions.query(
            DEFAULT_SUBSCRIPTIONS_TABLE,
            filters={'account_id': account_id, 'id': subscription_id})
    except RqlRuntimeError as runtime_err:
        return runtime_err
    except RqlDriverError as rql_err:
        return rql_err


def validate_access(username, registration_id=None, subscription_id=None,
                    incoming_account_id=None):
    """
    Validate access to resources
    """
    if username == 'admin':
        return None

    account_id = lookup_account_id(username)

    try:
        if registration_id:
            if not lookup_registration_id(account_id, registration_id):
                return make_response(
                    jsonify({'Error': 'Not authorized'}), client.UNAUTHORIZED)
        if subscription_id:
            if not lookup_subscription_id(account_id, subscription_id):
                return make_response(
                    jsonify({'Error': 'Not authorized'}), client.UNAUTHORIZED)
        if incoming_account_id:
            if incoming_account_id != account_id:
                return make_response(
                    jsonify({'Error': 'Not authorized'}), client.UNAUTHORIZED)
    except (RqlRuntimeError, RqlDriverError, Exception):
        return make_response(
            jsonify({'Error': 'Account or registration record not found'}),
            client.NOT_FOUND)

    return None


def registration_id_exists(registration_id):
    """
    Looks up registration based on record_id and pass the record back
    """
    try:
        registration = Interactions.query(
            DEFAULT_REGISTRATIONS_TABLE, filters={'id': registration_id})
        if registration:
            return True
        return False
    except RqlRuntimeError as runtime_err:
        return runtime_err
    except RqlDriverError as rql_err:
        return rql_err
