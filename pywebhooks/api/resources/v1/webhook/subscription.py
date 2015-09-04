# Standard lib imports
from http import client

# Third-party imports
from flask import request, jsonify, make_response
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks import DEFAULT_SUBSCRIPTIONS_TABLE
from pywebhooks.api.handlers.pagination_handler import paginate
from pywebhooks.api.handlers.resources_handler import insert, delete, \
    registration_id_exists, lookup_account_id, validate_access
from pywebhooks.api.decorators.authorization import api_key_restricted_resource
from pywebhooks.api.decorators.validation import validate_pagination_params, \
    validate_id_params


class Subscription(Resource):
    """
    Handles the (webhook) subscriptions table interactions
    """

    @api_key_restricted_resource(verify_admin=False)
    @validate_pagination_params()
    def get(self):
        """
        Get the user's webhook subscriptions
        """
        try:
            account_id = lookup_account_id(request.headers['username'])
        # pylint: disable=W0703
        except Exception:
            return make_response(
                jsonify({'Error': 'Invalid username or account'}),
                client.BAD_REQUEST)

        return paginate(request, DEFAULT_SUBSCRIPTIONS_TABLE, 'subscriptions',
                        filters={'account_id': account_id})

    @validate_id_params('subscription_id')
    @api_key_restricted_resource(verify_admin=False)
    def post(self, subscription_id):
        """
        Creates new subscription
        """
        # subscription_id is actually the registration_id
        registration_id = subscription_id

        account_id = lookup_account_id(request.headers['username'])

        if not registration_id_exists(registration_id):
            return make_response(
                jsonify({'Error': 'The registration id does not exist'}),
                client.NOT_FOUND)

        return insert(DEFAULT_SUBSCRIPTIONS_TABLE,
                      **{'account_id': account_id,
                         'registration_id': registration_id})

    @validate_id_params('subscription_id')
    @api_key_restricted_resource(verify_admin=False)
    def delete(self, subscription_id):
        """
        Deletes subscription record
        """
        return_val = validate_access(
            request.headers['username'],
            subscription_id=subscription_id)

        if return_val:
            return return_val

        return delete(DEFAULT_SUBSCRIPTIONS_TABLE, subscription_id)
