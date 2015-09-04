# Standard lib imports
from http import client

# Third-party imports
from flask import request, jsonify, make_response
from flask.ext.restful import Resource

# Project-level imports
from pywebhooks import DEFAULT_TRIGGERED_TABLE, DEFAULT_REGISTRATIONS_TABLE, \
    DEFAULT_SUBSCRIPTIONS_TABLE, DEFAULT_ACCOUNTS_TABLE, MAX_FAILED_COUNT
from pywebhooks.api.decorators.authorization import api_key_restricted_resource
from pywebhooks.api.decorators.validation import validate_pagination_params, \
    validate_id_params
from pywebhooks.api.handlers.resources_handler import insert, \
    lookup_account_id, lookup_registration_id
from pywebhooks.api.handlers.pagination_handler import paginate
from pywebhooks.database.rethinkdb.interactions import Interactions


class TriggeredAPI(Resource):

    @validate_pagination_params()
    @api_key_restricted_resource(verify_admin=False)
    def get(self):
        """
        Get a listing of triggered webhooks (paginated if need be)
        """
        return paginate(request, DEFAULT_TRIGGERED_TABLE, 'triggered_webhooks')

    @validate_id_params('registration_id')
    @api_key_restricted_resource(verify_admin=False)
    def post(self, registration_id):
        """
        Creates new triggered webhook event
        """
        registration = Interactions.query(
            DEFAULT_REGISTRATIONS_TABLE, filters={'id': registration_id})

        if not registration:
            return make_response(
                jsonify(
                    {'Error': 'Registration id not found'}
                ), client.NOT_FOUND)

        # Other users cannot trigger webhooks they didn't create
        calling_account_id = lookup_account_id(request.headers['username'])

        if not lookup_registration_id(calling_account_id, registration_id):
            return make_response(
                jsonify({'Error': 'You don\'t have access '
                                  'to this registration record or it no '
                                  'longer exists'}),
                client.UNAUTHORIZED)

        # Notify subscribed endpoints (send the webhooks out)
        subscriptions = Interactions.list_all(
            DEFAULT_SUBSCRIPTIONS_TABLE, order_by='epoch',
            filters={'registration_id': registration_id})

        if subscriptions:
            for record in subscriptions:
                account = Interactions.get(DEFAULT_ACCOUNTS_TABLE,
                                           record['account_id'])
                # Only hit the endpoint if their failed count is low enough
                if int(account['failed_count']) < MAX_FAILED_COUNT:
                    # This import is required to be here so the flask-restful
                    # piece works properly with Celery
                    from pywebhooks.tasks.webhook_notification import \
                        notify_subscribed_accounts

                    notify_subscribed_accounts.delay(
                        event=registration[0]['event'],
                        event_data=registration[0]['event_data'],
                        secret_key=account['secret_key'],
                        endpoint=account['endpoint'],
                        account_id=record['account_id'])

        return insert(DEFAULT_TRIGGERED_TABLE,
                      **{'registration_id': registration_id})
