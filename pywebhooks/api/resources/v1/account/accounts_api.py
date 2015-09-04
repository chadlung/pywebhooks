# Standard lib imports
# None
# Third-party imports
from flask import request
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks import DEFAULT_ACCOUNTS_TABLE
from pywebhooks.api.decorators.authorization import api_key_restricted_resource
from pywebhooks.api.handlers.pagination_handler import paginate
from pywebhooks.api.handlers.resources_handler import \
    delete_accounts_except_admins
from pywebhooks.api.decorators.validation import validate_pagination_params


class AccountsAPI(Resource):
    """
    Handles the REST API interaction for accounts
    """

    @api_key_restricted_resource(verify_admin=True)
    @validate_pagination_params()
    def get(self):
        """
        Get a listing of accounts (paginated if need be)
        """
        return paginate(request, DEFAULT_ACCOUNTS_TABLE, 'accounts')

    @api_key_restricted_resource(verify_admin=True)
    def delete(self):
        """
        Deletes all records (except admin) in the Accounts table
        """
        return delete_accounts_except_admins()
