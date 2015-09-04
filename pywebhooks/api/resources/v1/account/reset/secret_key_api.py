# Standard lib imports
# None

# Third-party imports
from flask import request
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks.api.handlers.resources_handler import reset_key
from pywebhooks.api.decorators.authorization import api_key_restricted_resource


class SecretKeyAPI(Resource):
    """
    Handles the REST API interaction for resetting secret keys
    """

    @api_key_restricted_resource()
    def post(self):
        """
        Resets a secret key
        """
        return reset_key(request.headers['username'], 'secret_key')
