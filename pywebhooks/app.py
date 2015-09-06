# Standard lib imports
import argparse

# Third-party imports
from celery import Celery
from pywebhooks import CELERY_BROKER_URL


from flask import Flask, request
from flask.ext.restful import Api

# Project-level imports
from pywebhooks.api.resources.v1.account.account_api import AccountAPI
from pywebhooks.api.resources.v1.account.accounts_api import AccountsAPI
from pywebhooks.api.resources.v1.webhook.registration_api import \
    RegistrationAPI
from pywebhooks.api.resources.v1.webhook.registrations_api import \
    RegistrationsAPI
from pywebhooks.api.resources.v1.account.reset.secret_key_api import \
    SecretKeyAPI
from pywebhooks.api.resources.v1.account.reset.api_key_api import ApiKeyAPI
from pywebhooks.api.resources.v1.webhook.subscription import Subscription
from pywebhooks.api.resources.v1.webhook.subscriptions import Subscriptions
from pywebhooks.api.resources.v1.webhook.triggered_api import TriggeredAPI
from pywebhooks.database.rethinkdb.initialize import create_database
from pywebhooks.database.rethinkdb.drop import drop_database
from pywebhooks.database.rethinkdb.bootstrap_admin import create_admin_account


def create_wsgi_app():
    flask_app = Flask(__name__)
    flask_app.url_map.strict_slashes = False
    api = Api(flask_app)

    api.add_resource(AccountsAPI, '/v1/accounts')
    api.add_resource(AccountAPI, '/v1/account/<account_id>', '/v1/account')

    api.add_resource(SecretKeyAPI, '/v1/account/reset/secretkey')

    api.add_resource(ApiKeyAPI, '/v1/account/reset/apikey')

    api.add_resource(RegistrationAPI, '/v1/webhook/registration',
                     '/v1/webhook/registration/<registration_id>')
    api.add_resource(RegistrationsAPI, '/v1/webhook/registrations')

    api.add_resource(TriggeredAPI, '/v1/webhook/triggered',
                     '/v1/webhook/triggered/<registration_id>')

    api.add_resource(Subscriptions, '/v1/webhook/subscriptions')
    api.add_resource(Subscription, '/v1/webhook/subscription',
                     '/v1/webhook/subscription/<subscription_id>')

    # There is no need for rate limits so it can be turned off
    flask_app.config['CELERY_DISABLE_RATE_LIMITS'] = True
    CELERY.conf.update(flask_app.config)

    return flask_app


CELERY = Celery(__name__, broker=CELERY_BROKER_URL)
app = create_wsgi_app()


@app.before_request
def before_request():
    if request.headers['content-type'].lower().find('application/json'):
        return 'Unsupported Media Type', 415


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser(description='Run the PyWebHooks app')
    parser.add_argument('--initdb', dest='initdb', action='store_true')
    args = parser.parse_args()

    if args.initdb:
        print('Dropping database...')
        drop_database()
        print('Creating database...')
        create_database()
        print('Adding admin account')
        print(create_admin_account())
        print('Complete')
    else:
        app.run(debug=True, port=8081)
