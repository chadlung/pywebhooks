# Standard lib imports
from http import client

# Third-party imports
from flask import request, jsonify, make_response
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.api.decorators.authorization import api_key_restricted_resource
from pywebhooks.api.handlers.resources_handler import client_echo_valid, \
    insert_account, delete_account, update, query, lookup_account_id, \
    validate_access
from pywebhooks.utils.common import generate_key
from pywebhooks.api.decorators.validation import validate_id_params


class AccountAPI(Resource):
    """
    Handles the REST API interaction for accounts
    """

    @validate_id_params('account_id')
    @api_key_restricted_resource(verify_admin=False)
    def get(self, account_id):
        """
        Gets a user account. Users can only see their own account
        """
        if lookup_account_id(request.headers['username']) == account_id:
            return query(DEFAULT_ACCOUNTS_TABLE, account_id)
        else:
            return make_response(jsonify(
                {'Error': 'Not authorized'}),
                client.UNAUTHORIZED)

    @api_key_restricted_resource(verify_admin=False)
    def patch(self):
        """
        Updates account. Only one field can be updated: endpoint
        Updating the endpoint also resets the failed_count
        """
        json_data = request.get_json()
        username = request.headers['username']

        if 'endpoint' in json_data:
            update_json = {
                'endpoint': json_data['endpoint'],
                'failed_count': 0
            }
        else:
            return make_response(jsonify(
                {'Error': 'Missing endpoint field'}), client.BAD_REQUEST)

        return update(DEFAULT_ACCOUNTS_TABLE, username=username,
                      updates=update_json)

    def post(self):
        """
        Creates a new account
        """
        json_data = request.get_json()

        if not client_echo_valid(json_data['endpoint']):
            return make_response(jsonify({'Error': 'Echo response failed'}),
                                 client.BAD_REQUEST)

        return insert_account(DEFAULT_ACCOUNTS_TABLE,
                              **{'username': json_data['username'],
                                 'endpoint': json_data['endpoint'],
                                 'is_admin': False,
                                 'failed_count': 0,
                                 'api_key': generate_key(),
                                 'secret_key': generate_key()})

    @validate_id_params('account_id')
    @api_key_restricted_resource(verify_admin=False)
    def delete(self, account_id):
        """
        Deletes account record
        """
        return_val = validate_access(
            request.headers['username'],
            incoming_account_id=account_id)

        if return_val:
            return return_val

        return delete_account(account_id)
