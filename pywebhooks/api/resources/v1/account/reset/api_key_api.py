# Standard lib imports
# None

# Third-party imports
from flask import request
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks.api.handlers.resources_handler import reset_key
from pywebhooks.api.decorators.validation import validate_username_in_header


class ApiKeyAPI(Resource):
    """
    Handles the REST API interaction for resetting api keys
    """

    @validate_username_in_header()
    def post(self):
        """
        Resets an api key
        """
        return reset_key(request.headers['username'], 'api_key')
