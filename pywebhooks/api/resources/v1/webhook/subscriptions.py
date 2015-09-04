# Standard lib imports

# Third-party imports
from flask import request
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks import DEFAULT_SUBSCRIPTIONS_TABLE
from pywebhooks.api.decorators.authorization import api_key_restricted_resource
from pywebhooks.api.handlers.resources_handler import delete_all
from pywebhooks.api.handlers.pagination_handler import paginate
from pywebhooks.api.decorators.validation import validate_pagination_params


class Subscriptions(Resource):
    """
    Handles the (webhook) subscriptions table interactions
    """

    @validate_pagination_params()
    @api_key_restricted_resource(verify_admin=False)
    def get(self):
        """
        Get a listing of subscriptions (paginated if need be)
        """
        return paginate(request, DEFAULT_SUBSCRIPTIONS_TABLE, 'subscriptions')

    @api_key_restricted_resource(verify_admin=True)
    def delete(self):
        """
        Deletes all records in the subscriptions table
        """
        return delete_all(DEFAULT_SUBSCRIPTIONS_TABLE)
