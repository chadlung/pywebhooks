# flake8: noqa

# Standard lib imports
# None

# Third-party imports
# None

# Project-level imports
from pywebhooks.database.rethinkdb.initialize import create_database
from pywebhooks.database.rethinkdb.drop import drop_database
from pywebhooks.database.rethinkdb.bootstrap_admin import create_admin_account
from pywebhooks.utils.request_handler import RequestHandler


BASE_URL = 'http://127.0.0.1:8081/v1/{0}'


def initdb():
    drop_database()
    create_database()
    return create_admin_account()


def create_account_records(request_handler):
    url = BASE_URL.format('account')
    user_keys = {}

    accounts = [{'username': 'johndoe',
                 'endpoint': 'http://127.0.0.1:9090/account/endpoint'},
                {'username': 'janedoe',
                 'endpoint': 'http://127.0.0.1:9090/account/endpoint'},
                {'username': 'samjones',
                 'endpoint': 'http://127.0.0.1:9090/account/endpoint'},
                {'username': 'leahrichards',
                 'endpoint': 'http://127.0.0.1:9090/account/endpoint'}]

    for account in accounts:
        data, status_code = request_handler.post(url, account)
        # Store the generated api and secret keys
        user_keys[account['username']] = {'api_key': data['api_key'],
                                          'secret_key': data['secret_key'],
                                          'id': data['id']}
    return user_keys


def get_accounts_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('accounts')

    data, status_code = request_handler.get(
        url, params={'start': 0, 'limit': 20},
        api_key=api_key, username=username)
    return data, status_code


def reset_key(request_handler, username=None, api_key=None, key_type='api_key'):
    if key_type == 'api_key':
        url = BASE_URL.format('account/reset/apikey')
    else:
        url = BASE_URL.format('account/reset/secretkey')

    data, status_code = request_handler.post(
        url, username=username, api_key=api_key)
    return data, status_code


def update_account_record(request_handler, username=None, api_key=None,
                          endpoint=None):
    url = BASE_URL.format('account')

    data, status_code = request_handler.patch(
        url, json_payload={'endpoint': endpoint},
        username=username,
        api_key=api_key)
    return data, status_code


def get_account_record(request_handler, username=None, api_key=None,
                       account_id=None):
    account_url = 'account/{0}'.format(account_id)
    url = BASE_URL.format(account_url)

    data, status_code = request_handler.get(url, username=username, api_key=api_key)
    return data, status_code


def delete_account_record(request_handler, username=None, api_key=None,
                          account_id=None):
    account_url = 'account/{0}'.format(account_id)
    url = BASE_URL.format(account_url)

    data, status_code = request_handler.delete(
        url, username=username, api_key=api_key)
    return data, status_code


def delete_accounts_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('accounts')

    data, status_code = request_handler.delete(
        url, username=username, api_key=api_key)
    return data, status_code


def insert_registration_record(request_handler, username=None, api_key=None,
                               json_payload={}):
    url = BASE_URL.format('webhook/registration')

    data, status_code = request_handler.post(
        url, username=username, api_key=api_key, json_payload=json_payload)
    return data, status_code


def get_registration_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('webhook/registration')

    data, status_code = request_handler.get(
        url, params={'start': 0, 'limit': 20},
        username=username, api_key=api_key)
    return data, status_code


def get_registrations_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('webhook/registrations')

    data, status_code = request_handler.get(
        url, params={'start': 0, 'limit': 20},
        username=username, api_key=api_key)
    return data, status_code


def update_registration_record(request_handler, username=None, api_key=None,
                               registration_id=None, json_payload={}):
    registration_url = 'webhook/registration/{0}'.format(registration_id)
    url = BASE_URL.format(registration_url)

    data, status_code = request_handler.patch(
        url, json_payload=json_payload, username=username, api_key=api_key)
    return data, status_code


def delete_registration_record(request_handler, username=None, api_key=None,
                               registration_id=None):
    registration_url = 'webhook/registration/{0}'.format(registration_id)
    url = BASE_URL.format(registration_url)

    data, status_code = request_handler.delete(
        url, username=username, api_key=api_key)
    return data, status_code


def delete_registrations_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('webhook/registrations')

    data, status_code = request_handler.delete(
        url, username=username, api_key=api_key)
    return data, status_code


def get_subscription_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('webhook/subscription')

    data, status_code = request_handler.get(
        url,params={'start': 0, 'limit': 20},
        username=username, api_key=api_key)
    return data, status_code


def insert_subscription_record(request_handler, username=None, api_key=None,
                               registration_id=None):
    registration_url = 'webhook/subscription/{0}'.format(registration_id)
    url = BASE_URL.format(registration_url)

    data, status_code = request_handler.post(
        url, username=username, api_key=api_key)
    return data, status_code


def get_subscriptions_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('webhook/subscriptions')

    try:
        data, status_code = request_handler.get(
            url,params={'start': 0, 'limit': 20},
            username=username, api_key=api_key)
    except ValueError:
        # No records are left
        return None, 204

    return data, status_code


def delete_subscriptions_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('webhook/subscriptions')

    data, status_code = request_handler.delete(
        url, username=username, api_key=api_key)
    return data, status_code


def delete_subscription_record(request_handler, username=None, api_key=None,
                               subscription_id=None):
    subscription_url = 'webhook/subscription/{0}'.format(subscription_id)
    url = BASE_URL.format(subscription_url)

    data, status_code = request_handler.delete(
        url, username=username, api_key=api_key)
    return data, status_code


def insert_triggered_record(request_handler, username=None, api_key=None,
                            registration_id=None):
    registration_url = 'webhook/triggered/{0}'.format(registration_id)
    url = BASE_URL.format(registration_url)

    data, status_code = request_handler.post(
        url, username=username, api_key=api_key)
    return data, status_code


def get_triggered_records(request_handler, username=None, api_key=None):
    url = BASE_URL.format('webhook/triggered')

    data, status_code = request_handler.get(url,
                                            params={'start': 0, 'limit': 20},
                                            username=username,
                                            api_key=api_key)
    return data, status_code


def validate_account_actions(request_handler, users_and_keys=None,
                             admin_username=None, admin_api_key=None):
    john_doe_info = users_and_keys['johndoe']
    jane_doe_info = users_and_keys['janedoe']
    sam_jones_info = users_and_keys['samjones']

    # Regular (non-admin) users should not be able to list accounts
    _, status = get_accounts_records(request_handler, username='johndoe',
                                     api_key=john_doe_info['api_key'])
    assert status == 401

    # Reset a secret key
    _, status = reset_key(request_handler, username='samjones',
                          api_key=sam_jones_info['api_key'],
                          key_type='secret_key')
    assert status == 200

    # Reset an API key
    _, status = reset_key(request_handler, username='samjones',
                          key_type='api_key')
    assert status == 200

    # Update an endpoint
    json_data, status = update_account_record(
        request_handler, 'johndoe', api_key=john_doe_info['api_key'],
        endpoint='http://127.0.0.1:9090/account/alternate/endpoint')

    assert status == 200
    assert json_data['replaced'] == 1

    # Get a single account record (johndoe)
    json_data, status = get_account_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        account_id=john_doe_info['id'])

    assert status == 200
    assert json_data['username'] == 'johndoe'

    # Users should not be able to get someone else's account record
    json_data, status = get_account_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        account_id=jane_doe_info['id'])

    assert status == 401

    # User's should not be able to delete another user's account record
    _, status = delete_account_record(
        request_handler,
        username='johndoe',
        api_key=john_doe_info['api_key'],
        account_id=sam_jones_info['id'])
    assert status == 401

    # Admin can delete any account record
    json_data, status = delete_account_record(
        request_handler,
        username=admin_username,
        api_key=admin_api_key,
        account_id=sam_jones_info['id'])
    assert status == 200
    assert json_data['deleted'] == 1


def validate_misc_actions(request_handler, users_and_keys=None):
    sam_jones_info = users_and_keys['samjones']
    leah_richards_info = users_and_keys['leahrichards']

    # Insert new leah richards registration record
    json_data, status = insert_registration_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        json_payload={'event': 'leahrichards.event',
                      'description': 'leah richards registered webhook',
                      'event_data': {'message': 'Leah Richards'}})
    assert status == 201
    leah_richards_registration_id = json_data['id']

    # User's should not be able to update another user's registration
    json_data, status = update_registration_record(
        request_handler, username='leahrichards',
        api_key=sam_jones_info['api_key'],
        registration_id=leah_richards_registration_id,
        json_payload={'description': 'leah new'})
    assert status == 401

    # User's should be able to delete their own account
    json_data, status = delete_account_record(
        request_handler,
        username='samjones',
        api_key=sam_jones_info['api_key'],
        account_id=sam_jones_info['id'])
    assert status == 200
    assert json_data['deleted'] == 1


def validate_registration_actions(request_handler, users_and_keys=None):
    john_doe_info = users_and_keys['johndoe']
    jane_doe_info = users_and_keys['janedoe']
    leah_richards_info = users_and_keys['leahrichards']

    # Insert new janedoe registration record
    json_data, status = insert_registration_record(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'],
        json_payload={'event': 'janedoe.event',
                      'description': 'jane doe registered webhook',
                      'event_data': {'message': 'Jane Doe'}})

    assert status == 201
    jane_doe_registration_id = json_data['id']

    # Get the user's registration record(s)
    json_data, status = get_registration_records(request_handler,
                                                 'janedoe',
                                                 jane_doe_info['api_key'])

    assert 'registrations' in json_data
    assert len(json_data['registrations']) == 1

    # Insert new johndoe registration record
    json_data, status = insert_registration_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        json_payload={'event': 'johndoe.event',
                      'description': 'john doe registered webhook',
                      'event_data': {'message': 'John Doe'}})

    assert status == 201
    john_doe_registration_id = json_data['id']

    # Get the user's registration record(s)
    json_data, status = get_registration_records(request_handler,
                                                 'johndoe',
                                                 john_doe_info['api_key'])

    assert 'registrations' in json_data
    assert len(json_data['registrations']) == 1

    # Insert new leahrichards registration record
    json_data, status = insert_registration_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        json_payload={'event': 'leahrichards.event',
                      'description': 'leah richards registered webhook',
                      'event_data': {'message': 'Leah Richards'}})

    assert status == 201
    leah_richards_registration_id = json_data['id']

    # Get all registrations (should be 3 of them)
    json_data, status = get_registrations_records(
        request_handler, 'leahrichards', leah_richards_info['api_key'])

    assert 'registrations' in json_data
    assert len(json_data['registrations']) == 3

    # Update a registration record (description)
    json_data, status = update_registration_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=leah_richards_registration_id,
        json_payload={'description': 'leah new'})

    assert status == 200
    assert json_data['replaced'] == 1

    json_data, status = get_registration_records(
        request_handler, 'leahrichards', leah_richards_info['api_key'])

    assert len(json_data['registrations']) == 1
    assert json_data['registrations'][0]['description'] == 'leah new'

    # Delete registration record
    json_data, status = delete_registration_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=leah_richards_registration_id)

    assert status == 200
    assert json_data['deleted'] == 1

    # Another user should not be able to delete someone else's
    # registration record
    _, status = delete_registration_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        registration_id=leah_richards_registration_id)

    assert status == 401

    # Get all registrations (should be 2 of them)
    json_data, status = get_registrations_records(
        request_handler, 'johndoe', john_doe_info['api_key'])

    assert len(json_data['registrations']) == 2

    return {
        'janedoe': jane_doe_registration_id,
        'johndoe': john_doe_registration_id,
        'leahrichards': leah_richards_registration_id
    }


def validate_subscription_actions(request_handler, users_and_keys=None,
                                  registration_ids=None,
                                  admin_username=None, admin_api_key=None):
    john_doe_info = users_and_keys['johndoe']
    jane_doe_info = users_and_keys['janedoe']
    leah_richards_info = users_and_keys['leahrichards']

    # You should not be able to create a new subscription with a
    # registration id that doesn't exist
    json_data, status = insert_subscription_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        registration_id='01d248ae-babb-4802-8060-47820c3bd018')

    assert status == 404

    # Create a new subscription
    json_data, status = insert_subscription_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        registration_id=registration_ids['janedoe'])

    # John Doe has subscribed to Jane Doe's webhook
    assert status == 201
    assert json_data['registration_id'] == registration_ids['janedoe']
    assert json_data['account_id'] == john_doe_info['id']
    john_doe_subscription_id = json_data['id']

    # Another user should not be able to delete someone else's
    # registration record. Jane Doe should not be able to delete
    # John Doe's subscription
    _, status = delete_subscription_record(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'],
        subscription_id=john_doe_subscription_id)

    assert status == 401

    # Insert new leahrichards registration record
    json_data, status = insert_registration_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        json_payload={'event': 'leahrichards.event',
                      'description': 'leah richards registered webhook',
                      'event_data': {'message': 'Leah Richards'}})

    assert status == 201

    # Create a new subscription
    json_data, status = insert_subscription_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        registration_id=registration_ids['janedoe'])

    # John Doe has subscribed to Leah Richard's webhook
    assert status == 201
    assert json_data['registration_id'] == registration_ids['janedoe']
    assert json_data['account_id'] == john_doe_info['id']

    # Get john doe's subscriptions (should be two, leah's and janes')
    json_data, status = get_subscription_records(
         request_handler, username='johndoe',
         api_key=john_doe_info['api_key'])

    assert status == 200
    assert 'subscriptions' in json_data
    assert len(json_data['subscriptions']) == 2

    # If we delete john doe's account record the subscriptions and
    # registrations should be gone as well
    # First, get a count of all registrations (should be 3)
    json_data, _ = get_registrations_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['registrations']) == 3

    # Get a count of all subscription records (should be 2)
    json_data, status = get_subscriptions_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['subscriptions']) == 2

    json_data, status = delete_account_record(
        request_handler, username=admin_username, api_key=admin_api_key,
        account_id=john_doe_info['id'])

    assert status == 200
    assert json_data['deleted'] == 1

    # Get a count of all registrations (should be 2)
    json_data, _ = get_registrations_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['registrations']) == 2

    # Get a count of all subscription records
    json_data, status = get_subscriptions_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert json_data is None

    # Create a new subscription (for delete check later)
    _, status = insert_subscription_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=registration_ids['janedoe'])

    assert status == 201


def validate_accounts_creation(request_handler, username=None, api_key=None):
        # List accounts, there should be 5 accounts, the admin and 4 users
        json_data, status = get_accounts_records(request_handler,
                                                 username=username,
                                                 api_key=api_key)

        assert len(json_data['accounts']) == 5
        assert status == 200


def validate_chain_scenario_one(request_handler, users_and_keys=None):
    john_doe_info = users_and_keys['johndoe']
    jane_doe_info = users_and_keys['janedoe']
    sam_jones_info = users_and_keys['samjones']
    leah_richards_info = users_and_keys['leahrichards']

    # John Doe will create a registration and everyone will subscribe it it
    json_data, status = insert_registration_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        json_payload={'event': 'johndoe.event',
                      'description': 'john doe registered webhook',
                      'event_data': {'message': 'John Doe'}})

    assert status == 201
    john_doe_registration_id = json_data['id']

    # Everyone subscribes including John Doe
    # JOHN DOE:
    json_data, status = insert_subscription_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    # JANE DOE:
    json_data, status = insert_subscription_record(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    # SAM JONES:
    json_data, status = insert_subscription_record(
        request_handler, username='samjones',
        api_key=sam_jones_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    # LEAH RICHARDS:
    json_data, status = insert_subscription_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201

    # Everyone has subscribed, now add one more registration that is not
    # john doe's and have leah richards subscribe to it, this subscription
    # should not be deleted
    # Jane Doe's new registration
    json_data, status = insert_registration_record(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'],
        json_payload={'event': 'janedoe.event',
                      'description': 'jane doe registered webhook',
                      'event_data': {'message': 'Jane Doe'}})

    assert status == 201
    jane_doe_registration_id = json_data['id']

    # Leah Richards subscribes to Jane Doe's webhook:
    json_data, status = insert_subscription_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=jane_doe_registration_id)
    assert status == 201

    # There should now be 2 registrations
    json_data, _ = get_registrations_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['registrations']) == 2

    # There should now be 5 subscriptions
    json_data, _ = get_subscriptions_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['subscriptions']) == 5

    # Delete John Doe's registration
    json_data, status = delete_registration_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        registration_id=john_doe_registration_id)

    assert status == 200
    assert json_data['deleted'] == 1

    # There should now be 1 registration
    json_data, _ = get_registrations_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['registrations']) == 1
    # That last subscription should belong to Jane Doe
    assert json_data['registrations'][0]['account_id'] == \
        jane_doe_info['id']

    # There should now be 1 subscription
    json_data, _ = get_subscriptions_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['subscriptions']) == 1
    # That last subscription should belong to Leah Richard
    assert json_data['subscriptions'][0]['account_id'] == \
        leah_richards_info['id']


def validate_chain_scenario_two(request_handler, users_and_keys=None,
                                admin_username=None, admin_api_key=None):
    john_doe_info = users_and_keys['johndoe']
    jane_doe_info = users_and_keys['janedoe']
    sam_jones_info = users_and_keys['samjones']
    leah_richards_info = users_and_keys['leahrichards']

    # Like scenario #1, John Doe will create a registration and everyone
    # will subscribe it it
    json_data, status = insert_registration_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        json_payload={'event': 'johndoe.event',
                      'description': 'john doe registered webhook',
                      'event_data': {'message': 'John Doe'}})

    assert status == 201
    john_doe_registration_id = json_data['id']

    # Everyone subscribes including John Doe
    # JOHN DOE:
    json_data, status = insert_subscription_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    # JANE DOE:
    json_data, status = insert_subscription_record(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    # SAM JONES:
    json_data, status = insert_subscription_record(
        request_handler, username='samjones',
        api_key=sam_jones_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    # LEAH RICHARDS:
    json_data, status = insert_subscription_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201

    # Everyone has subscribed, now add one more registration that is not
    # john doe's and have leah richards subscribe to it, this subscription
    # should not be deleted
    # Jane Doe's new registration
    json_data, status = insert_registration_record(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'],
        json_payload={'event': 'janedoe.event',
                      'description': 'jane doe registered webhook',
                      'event_data': {'message': 'Jane Doe'}})

    assert status == 201
    jane_doe_registration_id = json_data['id']

    # Leah Richards subscribes to Jane Doe's webhook:
    json_data, status = insert_subscription_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=jane_doe_registration_id)
    assert status == 201

    # There should now be 2 registrations
    json_data, _ = get_registrations_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['registrations']) == 2

    # There should now be 5 subscriptions
    json_data, _ = get_subscriptions_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['subscriptions']) == 5

    # Delete John Doe's account
    json_data, status = delete_account_record(
        request_handler, username=admin_username,
        api_key=admin_api_key,
        account_id=john_doe_info['id'])

    assert status == 200
    assert json_data['deleted'] == 1

    # There should now be 1 registration
    json_data, _ = get_registrations_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['registrations']) == 1
    # That last subscription should belong to Jane Doe
    assert json_data['registrations'][0]['account_id'] == \
        jane_doe_info['id']

    # There should now be 1 subscription
    json_data, _ = get_subscriptions_records(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'])

    assert len(json_data['subscriptions']) == 1
    # That last subscription should belong to Leah Richard
    assert json_data['subscriptions'][0]['account_id'] == \
        leah_richards_info['id']


def validate_webhook_actions(request_handler, users_and_keys=None):
    john_doe_info = users_and_keys['johndoe']
    jane_doe_info = users_and_keys['janedoe']
    sam_jones_info = users_and_keys['samjones']
    leah_richards_info = users_and_keys['leahrichards']

    # John Doe will create a registration and everyone
    # will subscribe it it
    json_data, status = insert_registration_record(
        request_handler, username='johndoe',
        api_key=john_doe_info['api_key'],
        json_payload={'event': 'johndoe.event',
                      'description': 'john doe registered webhook',
                      'event_data': {'message': 'John Doe'}})

    assert status == 201
    john_doe_registration_id = json_data['id']

    # Everyone subscribes except John Doe
    # JANE DOE:
    json_data, status = insert_subscription_record(
        request_handler, username='janedoe',
        api_key=jane_doe_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    # SAM JONES:
    json_data, status = insert_subscription_record(
        request_handler, username='samjones',
        api_key=sam_jones_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    # LEAH RICHARDS:
    json_data, status = insert_subscription_record(
        request_handler, username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201

    # John Doe will trigger his registered webhook
    json_data, status = insert_triggered_record(
        request_handler,
        username='johndoe',
        api_key=john_doe_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 201
    assert json_data['registration_id'] == john_doe_registration_id

    # There should be one triggered webhook record
    json_data, status = get_triggered_records(
        request_handler,
        username='johndoe',
        api_key=john_doe_info['api_key']
    )
    assert status == 200
    assert 'triggered_webhooks' in json_data
    assert json_data['triggered_webhooks'][0]['registration_id'] == \
        john_doe_registration_id

    # Other people cannot trigger webhooks other than their own
    json_data, status = insert_triggered_record(
        request_handler,
        username='leahrichards',
        api_key=leah_richards_info['api_key'],
        registration_id=john_doe_registration_id)
    assert status == 401


def validate_table_deletions(request_handler, admin_username=None,
                             admin_api_key=None):
        json_data, status = delete_accounts_records(
            request_handler, username=admin_username, api_key=admin_api_key)
        assert status == 200
        assert json_data['deleted'] == 2

        json_data, status = delete_subscriptions_records(
            request_handler, username=admin_username, api_key=admin_api_key)
        assert status == 200
        assert json_data['deleted'] == 1

        json_data, status = delete_registrations_records(
            request_handler, username=admin_username, api_key=admin_api_key)
        assert status == 200
        assert json_data['deleted'] == 2


def perform_table_deletions(request_handler, admin_username=None,
                            admin_api_key=None):
        json_data, status = delete_accounts_records(
            request_handler, username=admin_username, api_key=admin_api_key)
        assert status == 200

        json_data, status = delete_subscriptions_records(
            request_handler, username=admin_username, api_key=admin_api_key)
        assert status == 200

        json_data, status = delete_registrations_records(
            request_handler, username=admin_username, api_key=admin_api_key)
        assert status == 200


def run_tests():
    """
    Running this code requires you have RethinkDB setup and running as well
    as Redis and the Celery worker. These tests should run through all the
    possible scenarios.
    """
    request_handler = RequestHandler(verify_ssl=False,
                                     request_timeout=10.0)

    print('Functional Testing Starting...')

    # Start with a clean database
    admin_account = initdb()

    admin_username = 'admin'
    admin_api_key = admin_account['api_key']

    # Create four user accounts
    users_and_keys = create_account_records(request_handler)

    # **********************************
    # *** Validate Account Creations ***
    # **********************************
    validate_accounts_creation(request_handler,
                               username=admin_username,
                               api_key=admin_api_key)

    # ********************************
    # *** Validate Account Actions ***
    # ********************************
    validate_account_actions(
        request_handler, users_and_keys=users_and_keys,
        admin_username=admin_username, admin_api_key=admin_api_key)

    # *************************************
    # *** Validate Registration Actions ***
    # *************************************
    user_registration_ids = validate_registration_actions(
        request_handler, users_and_keys=users_and_keys)

    # *************************************
    # *** Validate Subscription Actions ***
    # *************************************
    validate_subscription_actions(
        request_handler,
        users_and_keys=users_and_keys,
        registration_ids=user_registration_ids,
        admin_username=admin_username,
        admin_api_key=admin_api_key)

    # ***************************************
    # *** Validate Table Deletion Actions ***
    # ***************************************
    validate_table_deletions(
        request_handler,
        admin_username=admin_username,
        admin_api_key=admin_api_key)

    # *****************************************
    # *** Validate Chained Deletion Actions ***
    # *****************************************
    #
    # The database should be empty so run the more complex tests:
    #
    # 1.) When deleting a registration record it should also remove the records
    # for that registration_id in the subscription table
    #
    # 2.) When deleting an account it should delete that user's account,
    # registrations and subscriptions. It should also delete other user's
    # subscriptions to those registrations that were deleted
    #
    # Re-populate the users and test scenario #1
    validate_chain_scenario_one(
        request_handler,
        users_and_keys=create_account_records(request_handler))

    # Clean the tables out again (no need to count the deletes as this has been
    # tested prior
    perform_table_deletions(
        request_handler,
        admin_username=admin_username,
        admin_api_key=admin_api_key)
    # Re-populate the users and test scenario #2
    validate_chain_scenario_two(
        request_handler,
        users_and_keys=create_account_records(request_handler),
        admin_username=admin_username,
        admin_api_key=admin_api_key)

    # *******************************
    # *** Validate Misc. Actions ***
    # *******************************

    # Clean the tables out again (no need to count the deletes as this has been
    # tested prior
    perform_table_deletions(
        request_handler,
        admin_username=admin_username,
        admin_api_key=admin_api_key)
    # These are tests that don't work with the flow prior so they are on
    # their own
    validate_misc_actions(
        request_handler,
        users_and_keys=create_account_records(request_handler))

    # ********************************
    # *** Validate WebHook Actions ***
    # ********************************

    # Clean the tables out again (no need to count the deletes as this has been
    # tested prior
    perform_table_deletions(
        request_handler,
        admin_username=admin_username,
        admin_api_key=admin_api_key)

    validate_webhook_actions(
        request_handler,
        users_and_keys=create_account_records(request_handler))

    print('Functional Testing Complete')


if __name__ == "__main__":
    run_tests()
