# Standard lib imports
from http import client
from functools import wraps

# Third-party imports
from flask import request, jsonify, make_response

# Project-level imports
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions


def validate_pagination_params():
    """
    Validate the API Key and Username in the header
    Note: This is very basic authorization for a proof of concept
    """

    def decorated(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                limit = int(request.args.get('limit'))
                start = int(request.args.get('start'))

                if start > 999999999999999 or start < 0:
                    raise ValueError()
                if limit > 100 or limit <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return make_response(
                    jsonify({'Error': 'Invalid limit or start parameter'}),
                    client.BAD_REQUEST
                )

            return f(*args, **kwargs)

        return wrapper
    return decorated


def validate_username_in_header():
    """
    Validate that the username header is set and exists in the accounts table
    """

    def decorated(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                username = request.headers['username']
            except KeyError:
                return make_response(
                    jsonify(
                        {'Error': 'Missing the username header value'}
                    ), client.BAD_REQUEST
                )

            record = Interactions.query(DEFAULT_ACCOUNTS_TABLE,
                                        filters={'username': username})

            if not record:
                return make_response(
                    jsonify({'Error': 'Username not found'}), client.NOT_FOUND)

            return f(*args, **kwargs)

        return wrapper
    return decorated


def validate_id_params(param_name):
    """
    Validate the that the param_name is in the request
    """
    def decorated(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                if not kwargs.get(param_name):
                        return make_response(jsonify(
                            {'Error': 'Missing {0}'.format(param_name)}),
                            client.BAD_REQUEST)
            except Exception as ex:
                return make_response(
                    jsonify({'Error': ex}),
                    client.BAD_REQUEST
                )

            return f(*args, **kwargs)

        return wrapper
    return decorated
