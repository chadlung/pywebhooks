# Standard lib imports
from http import client

# Third-party imports
from flask import request, jsonify, make_response
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks import DEFAULT_REGISTRATIONS_TABLE
from pywebhooks.api.handlers.pagination_handler import paginate
from pywebhooks.api.handlers.resources_handler import lookup_account_id, \
    validate_access, delete_registration, insert, update
from pywebhooks.api.decorators.authorization import api_key_restricted_resource
from pywebhooks.api.decorators.validation import validate_pagination_params, \
    validate_id_params


class RegistrationAPI(Resource):

    @api_key_restricted_resource(verify_admin=False)
    @validate_pagination_params()
    def get(self):
        """
        Get the user's registered webhooks
        """
        account_id = lookup_account_id(request.headers['username'])

        return paginate(request, DEFAULT_REGISTRATIONS_TABLE, 'registrations',
                        filters={'account_id': account_id})

    @validate_id_params('registration_id')
    @api_key_restricted_resource(verify_admin=False)
    def patch(self, registration_id):
        """
        Updates registration. Only one field can be updated: description
        """
        return_val = validate_access(
            request.headers['username'],
            registration_id=registration_id)

        if return_val:
            return return_val

        json_data = request.get_json()
        update_json = {}

        if 'description' in json_data:
            update_json['description'] = json_data['description']
        else:
            return make_response(
                jsonify({'Error': 'Description field missing'}),
                client.BAD_REQUEST)

        return update(DEFAULT_REGISTRATIONS_TABLE,
                      record_id=registration_id,
                      updates=update_json)

    @api_key_restricted_resource(verify_admin=False)
    def post(self):
        """
        Creates a new registration
        """
        json_data = request.get_json()

        # Look up account id based on username, username will be valid since
        # the api_key_restricted_resource decorator runs first
        account_id = lookup_account_id(request.headers['username'])

        return insert(DEFAULT_REGISTRATIONS_TABLE,
                      **{'account_id': account_id,
                         'event': json_data['event'],
                         'description': json_data['description'],
                         'event_data': json_data['event_data']})

    @validate_id_params('registration_id')
    @api_key_restricted_resource(verify_admin=False)
    def delete(self, registration_id):
        """
        Deletes registration record, will also remove the records for this
        registration_id in the subscription table as well
        """
        return_val = validate_access(
            request.headers['username'],
            registration_id=registration_id)

        if return_val:
            return return_val

        return delete_registration(registration_id)
