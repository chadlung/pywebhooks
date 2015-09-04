# Standard lib imports
# None

# Third-party imports
from flask import request
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks import DEFAULT_REGISTRATIONS_TABLE
from pywebhooks.api.decorators.authorization import api_key_restricted_resource
from pywebhooks.api.handlers.pagination_handler import paginate
from pywebhooks.api.handlers.resources_handler import delete_all
from pywebhooks.api.decorators.validation import validate_pagination_params


class RegistrationsAPI(Resource):
    """
    Handles the REST API interaction for Registrations
    """

    @api_key_restricted_resource(verify_admin=False)
    @validate_pagination_params()
    def get(self):
        """
        Get a listing of Registrations (paginated if need be)
        """
        return paginate(request, DEFAULT_REGISTRATIONS_TABLE, 'registrations')

    @api_key_restricted_resource(verify_admin=True)
    def delete(self):
        """
        Deletes all records in the Registrations table
        """
        return delete_all(DEFAULT_REGISTRATIONS_TABLE)
