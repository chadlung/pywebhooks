# Standard lib imports
from http import client
from functools import wraps

# Third-party imports
from flask import request, jsonify, make_response
from werkzeug.security import check_password_hash

# Project-level imports
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.database.rethinkdb.interactions import Interactions


def api_key_restricted_resource(verify_admin=False):
    """
    Validate the API Key and Username in the header
    Note: This is very basic authorization for a proof of concept
    """

    def decorated(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                api_key = request.headers['api-key']
            except KeyError:
                return make_response(
                    jsonify(
                        {'Error': 'Missing API key header value'}
                    ), client.UNAUTHORIZED
                )

            try:
                username = request.headers['username']
            except KeyError:
                return make_response(
                    jsonify(
                        {'Error': 'Missing username header value'}
                    ), client.UNAUTHORIZED
                )

            record = Interactions.query(DEFAULT_ACCOUNTS_TABLE,
                                        filters={'username': username})

            if not record:
                return make_response(
                    jsonify({'Error': 'Invalid API key or Username'}),
                    client.UNAUTHORIZED
                )

            if not check_password_hash(record[0]['api_key'], api_key):
                return make_response(
                    jsonify({'Error': 'Invalid API key'}), client.UNAUTHORIZED)

            if verify_admin:
                if not record[0]['is_admin']:
                    return make_response(
                        jsonify({'Error': 'Not an Admin'}),
                        client.UNAUTHORIZED
                    )

            return f(*args, **kwargs)

        return wrapper
    return decorated
