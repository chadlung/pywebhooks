PyWebhooks
==========

*A simple webhooks service, minimal features, minimal security, proof of concept*

.. image:: https://travis-ci.org/chadlung/pywebhooks.svg?branch=master
    :target: https://travis-ci.org/chadlung/pywebhooks
.. image:: https://coveralls.io/repos/chadlung/pywebhooks/badge.svg?branch=master&service=github :target: https://coveralls.io/github/chadlung/pywebhooks?branch=master

**Note:** PyWebhooks is ideally deployed on an internal private cloud/network where you
know and trust the end users and services using it. It should not be considered
secure enough (currently) to be a publicly deployed service.

Don't like something? Need a feature? Please submit a pull request complete with
tests and an update to the readme if required.

In order to run PyWebhooks you'll need to have `RethinkDB <http://rethinkdb.com/>`__
and `Redis <http://redis.io/>`__ installed on a server or server(s). RethinkDB is
used to store the account, webooks, etc. data. Redis is used by
`Celery <http://http://www.celeryproject.org//>`__ to handle the calls to the
webhook endpoints.

**Note:** PyWebhooks has been tested on Ubuntu 14.04 and OS X.
PyWebhooks has been tested with Python 3.4.x and 3.5.x. Prior Python 3.x versions have not
been tested and Python 2.x support is not planned.

Why PyWebhooks?
^^^^^^^^^^^^^^^

I looked all over for a project that did something similar to this. You can find
lots of code to listen for webhooks as well as some code for sending webhooks
but I couldn't find anything that wrapped it into a complete package where you could
run a server to allow for adding new accounts, letting those users create their
own webhooks and then allow others to listen (subscribe) to those webhooks.

**TODOs:**

1. Add Logging

2. Change how config works

3. Add more unit tests

4. ... probably more

**Quick Start:** To get started quickly, see my introductory `blog article <http://www.giantflyingsaucer.com/blog/?p=5666>`__
as well as a helpful vagrant starter: `vagrant-pywebhooks <https://github.com/chadlung/vagrant-pywebhooks>`__

If you don't use the quick start mentioned above:

Once you have Redis and RethinkDB setup you can initialize the database and
admin accounts by running the following:

::

    $ python app.py --initdb

**Response:**

::

    Dropping database...
    Creating database...
    Adding admin account
    {'secret_key': 'a6d8ff11a7cdb51130ea184b7228e179f3fd3a4c', 'api_key': 'ba86c64c24f361ddbcfe27be187d8d3002c9f43c'}
    Complete

Make note of the admin ``api_key`` as it will be stored as a hash.

When you create a new user account there are a few things to consider. First,
you need to have an endpoint setup where the account creation process can verify
against. The endpoint can be whatever you want, a simple example would be a
service listening on: ``http://1270.0.1:9090/account/endpoint``

When you send the command to create the account if all goes well the PyWebhooks
server will hit the endpoint you specified with a challenge you need to echo back.
This helps ensure that you are actually setting up an endpoint that you control.

The PyWebhooks server will hit the endpoint you specified like this:
``/account/endpoint?echo=2cac9beaa2f3b3aa72cc86faefb7575ba9c3c4b8``

It is your server's job to take that echo value and return it. In Python (using Flask)
this would like:

::

    @app.route('/account/endpoint', methods=['GET'])
    def echo():
        return make_response(jsonify({'echo': request.args.get('echo')}), client.OK)

**Note:** PyWebhooks doesn't require your service be written in Python, any
language will do as long as it returns what is expected (in this case the echo value).

In Ruby 2.2.x using Sinatra a minimal endpoint server (handles Webhook POST traffic
and GET echo requests) might look like this:

::

    require 'rubygems'
    require 'openssl'
    require 'sinatra'
    require 'json'


    SHARED_SECRET = 'c27e823b0a500a537990dcccfc50334fe814fbd2'

    # Handle echo requests
    get '/account/endpoint' do
        content_type :json
        echo_value = params['echo']
        puts 'echo value:'
        puts(echo_value)

        status 200
        { :echo => echo_value }.to_json
    end

    # Handle the incoming webhook events
    post '/account/endpoint' do
      request.body.rewind
      data = request.body.read
      HMAC_DIGEST = OpenSSL::Digest.new('sha1')
      signature = OpenSSL::HMAC.hexdigest(HMAC_DIGEST, SHARED_SECRET, data)
      incoming_signature = env['HTTP_PYWEBHOOKS_SIGNATURE']

      puts 'hmac verification results:'
      puts Rack::Utils.secure_compare(signature, incoming_signature)

      incoming_event = env['HTTP_EVENT']
      puts 'incoming event is:'
      puts incoming_event
      puts 'incoming json is:'
      puts data

      status 200
      '{}'
    end


**Note:** Pardon my Ruby, I'm rusty with it.

A full Python 3.4 endpoint example server code (for testing) can be a simple as:

::

    import hashlib
    import hmac
    from http import client
    import json

    from flask import Flask
    from flask import request, make_response, jsonify


    app = Flask(__name__)

    # Adjust this as needed
    SECRET_KEY = 'c27e823b0a500a537990dcccfc50334fe814fbd2'


    def verify_hmac_hash(incoming_json, secret_key, incoming_signature):
        signature = hmac.new(
            str(secret_key).encode('utf-8'),
            str(incoming_json).encode('utf-8'),
            digestmod=hashlib.sha1
        ).hexdigest()

        return hmac.compare_digest(signature, incoming_signature)


    def create_response(req):
        if request.args.get('echo'):
            return make_response(jsonify({'echo': req.args.get('echo')}), client.OK)
        if request.args.get('api_key'):
            print('New api_key: {0}'.format(req.args.get('api_key')))
            return make_response(jsonify({}), client.OK)
        if request.args.get('secret_key'):
            print('New secret_key: {0}'.format(req.args.get('secret_key')))
            return make_response(jsonify({}), client.OK)


    def webhook_listener(request):
        print(request.headers)
        print(request.data)
        print(json.dumps(request.json))

        is_signature_valid = verify_hmac_hash(
            json.dumps(request.json),
            SECRET_KEY,
            request.headers['pywebhooks-signature']
        )

        print('Is Signature Valid?: {0}'.format(is_signature_valid))

        return make_response(jsonify({}), client.OK)


    @app.route('/account/endpoint', methods=['GET'])
    def echo():
        return create_response(request)


    @app.route('/account/alternate/endpoint', methods=['GET'])
    def echo_alternate():
        return create_response(request)


    @app.route('/account/alternate/endpoint', methods=['POST'])
    def account_alternate_listener():
        return webhook_listener(request)


    @app.route('/account/endpoint', methods=['POST'])
    def account_listener():
        return webhook_listener(request)


    if __name__ == '__main__':
        app.run(debug=True, port=9090)


You can save that code off into it's own project if you want just make sure to
install Flask.

Next, start one or more celery workers from the project root:

::

    $ celery -A pywebhooks.tasks.webhook_notification worker --loglevel=info

Start the main project in development mode:

::

    $ python app.py

With your endpoint service and Celery worker running you can now perform
the following calls.

Account Actions
^^^^^^^^^^^^^^^

**Creating an account:**

The examples below use human readable user names. The reality is you should use
a complex username to avoid any potential possibility of someone abusing the
``api_key`` reset as you only need a ``username`` to trigger a reset which could
allow for a denial of service on your endpoint. A complex username not shared
such as ``cRee82jfkjf09ij23`` is better than ``johndoe``. One potential fix
I will look at is limiting how many ``api_key`` resets can be done in a given
period (rate limiting).

::

    curl -v -X POST "http://127.0.0.1:8081/v1/account" -d '{"endpoint": "http://127.0.0.1:9090/account/endpoint", "username": "sarahfranks"}' -H "content-type: application/json"

**Response:**

**HTTP/1.0 201 CREATED**

::

    {
        "api_key": "be23d9ccb29082c489ba629077553ba1d8314005",
        "endpoint": "http://127.0.0.1:9090/account/endpoint",
        "epoch": 1441164550.515677,
        "id": "45712a61-a1b3-41a4-aa89-9593b909ae3d",
        "is_admin": false,
        "failed_count": 0,
        "secret_key": "5a4a1cf4895441a1dfaa504c471510be819198e7",
        "username": "sarahfranks"
     }

Make note of the ``id``, ``secret_key`` and ``api_key`` (because the ``api_key`` will be
stored hashed).

The ``secret_key`` will be used to validate the data coming into your endpoint
is indeed from the PyWebhooks server and not something/someone else.

The ``api_key`` will be used for any communication with the PyWebhooks server that
isn't a publicly accessible call.

The ``id`` will be the account id.

The ``failed_count`` field tracks how many times an attempt (webhook POST) has
failed to contact the specified endpoint. ``MAX_FAILED_COUNT`` is a config value
that can be set (default is 250). If the ``failed_count`` exceeds the
``MAX_FAILED_COUNT`` value then no more webhook posts will occur for the user
until this is reset. A successful endpoint contact will automatically reset
this value to 0 if ``MAX_FAILED_COUNT`` has not been exceeded. This helps
prevent an endpoint that is no longer responsive or moved (and not updated)
from continuing to utilize system resources. In addition, updating the endpoint
for a account will also reset the ``failed_count``.

Retries on webhook endpoints are done three times before giving up. The
``DEFAULT_RETRY`` config value (defaults to 2 minutes) and ``DEFAULT_FINAL_RETRY``
config value (defaults to 1 hour) can be adjusted for the three retries. Each
failed attempt to contact the endpoint results in an increment in the ``failed_count``
field of the user's account. If an endpoint is unreachable through the initial
attempt to contact and the three retires then the ``failed_count`` value will
be four.

**Get a single account record:**

You can only look-up your own account record.

::

    curl -v -X GET "http://127.0.0.1:8081/v1/account/45712a61-a1b3-41a4-aa89-9593b909ae3d" -H "content-type: application/json" -H "api-key: be23d9ccb29082c489ba629077553ba1d8314005" -H "username: sarahfranks"

**Response:**

**HTTP/1.0 200 OK**

::

    {
        "api_key": "pbkdf2:sha1:1000$vTuQRKeb$eec0bdffebde0d3c28290d41f4d848fbde04571c",
        "endpoint": "http://127.0.0.1:9090/account/endpoint",
        "epoch": 1441164550.515677,
        "id": "45712a61-a1b3-41a4-aa89-9593b909ae3d",
        "is_admin": false,
        "failed_count": 0,
        "secret_key": "5a4a1cf4895441a1dfaa504c471510be819198e7",
        "username": "sarahfranks"
    }

**Get all account records (admin only):**

This is a paginated call with ``start`` and ``limit`` params in the querystring.

**REQUIRED** ``start`` is where in the records you want to start listing (0..n)

**REQUIRED** ``limit`` is how many records to return

In the example below I started at record #0 and asked for up to 10 records to return.
You may also notice that a ``next_start`` field will show up in the JSON so you
know where to set your next start (assuming you want to keep paging the records)

::

    curl -v -X GET "http://127.0.0.1:8081/v1/accounts?start=0&limit=10" -H "content-type: application/json" -H "api-key: ba86c64c24f361ddbcfe27be187d8d3002c9f43c" -H "username: admin"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "accounts": [
        {
          "api_key": "pbkdf2:sha1:1000$rQDzv29j$5895b2393171d0cc238157c130fc2129d3e871c3",
          "endpoint": "",
          "epoch": 1441164269.341982,
          "id": "ed408f85-200e-481f-a672-30f454e8dcf4",
          "is_admin": true,
          "secret_key": "ab502753cbb68b90601cace345fe84fb2bb5b8dd",
          "username": "admin"
        },
        {
          "api_key": "pbkdf2:sha1:1000$I5r0MTsM$fc50fcce05c526fa19919d874087623571c0c9e0",
          "endpoint": "http://127.0.0.1:9090/account/endpoint",
          "epoch": 1441164337.607172,
          "id": "d969a56d-e520-405d-a24f-497ac6923781",
          "is_admin": false,
          "failed_count": 0,
          "secret_key": "2381a87ba4725786f29ca414d3217e202615f757",
          "username": "johndoe"
        },
        {
          "api_key": "pbkdf2:sha1:1000$an7K8KqL$127bb4796de21a832969512fc7c2edea0524e54b",
          "endpoint": "http://127.0.0.1:9090/account/endpoint",
          "epoch": 1441164337.630147,
          "id": "556daec0-fcad-4cae-8d4b-7564d2424669",
          "is_admin": false,
          "failed_count": 0,
          "secret_key": "25b83d9a713e16f1b4fe936787acdf532162ea73",
          "username": "janedoe"
        },
        {
          "api_key": "pbkdf2:sha1:1000$nbvEItNd$9d0ab21a122bca95855f6ba0ab271444168e17f4",
          "endpoint": "http://127.0.0.1:9090/account/endpoint",
          "epoch": 1441164337.65272,
          "id": "776236bc-5ca9-4083-bb20-b12043ec87de",
          "is_admin": false,
          "failed_count": 0,
          "secret_key": "d615166b1818ef41b925c40b5483474522bffc94",
          "username": "samjones"
        },
        {
          "api_key": "pbkdf2:sha1:1000$vTuQRKeb$eec0bdffebde0d3c28290d41f4d848fbde04571c",
          "endpoint": "http://127.0.0.1:9090/account/endpoint",
          "epoch": 1441164550.515677,
          "id": "45712a61-a1b3-41a4-aa89-9593b909ae3d",
          "is_admin": false,
          "failed_count": 0,
          "secret_key": "5a4a1cf4895441a1dfaa504c471510be819198e7",
          "username": "sarahfranks"
        }
      ]
    }

Example output with ``next_start``:

::

    curl -v -X GET "http://127.0.0.1:8081/v1/accounts?start=0&limit=3" -H "content-type: application/json" -H "api-key: 5b3a973f4980f65d5b61101ddf3b40808933f12a" -H "username: admin"

::

    {
      "accounts": [
        {
          "api_key": "pbkdf2:sha1:1000$rQDzv29j$5895b2393171d0cc238157c130fc2129d3e871c3",
          "endpoint": "",
          "epoch": 1441164269.341982,
          "id": "ed408f85-200e-481f-a672-30f454e8dcf4",
          "is_admin": true,
          "secret_key": "ab502753cbb68b90601cace345fe84fb2bb5b8dd",
          "username": "admin"
        },
        {
          "api_key": "pbkdf2:sha1:1000$I5r0MTsM$fc50fcce05c526fa19919d874087623571c0c9e0",
          "endpoint": "http://127.0.0.1:9090/account/endpoint",
          "epoch": 1441164337.607172,
          "id": "d969a56d-e520-405d-a24f-497ac6923781",
          "is_admin": false,
          "failed_count": 0,
          "secret_key": "2381a87ba4725786f29ca414d3217e202615f757",
          "username": "johndoe"
        },
        {
          "api_key": "pbkdf2:sha1:1000$an7K8KqL$127bb4796de21a832969512fc7c2edea0524e54b",
          "endpoint": "http://127.0.0.1:9090/account/endpoint",
          "epoch": 1441164337.630147,
          "id": "556daec0-fcad-4cae-8d4b-7564d2424669",
          "is_admin": false,
          "failed_count": 0,
          "secret_key": "25b83d9a713e16f1b4fe936787acdf532162ea73",
          "username": "janedoe"
        }
      ],
      "next_start": 3
    }

**Update the endpoint field for a username specified account:**

The only field that can be updated on an account is the ``endpoint`` and when you
do so PyWebhooks will contact that endpoint with the echo challenge as mentioned above
in the section on creating a new account.

**Note:** The ``api_key`` and ``secret_key`` can both be reset, those calls are
further down this document.

For this call you need to supply your username and ``api_key`` in the headers.

::

    curl -v -X PATCH "http://127.0.0.1:8081/v1/account" -d '{"endpoint": "http://127.0.0.1:9090/account/alternate/endpoint"}' -H "content-type: application/json" -H "api-key: d615166b1818ef41b925c40b5483474522bffc94" -H "username: samjones"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "deleted": 0,
      "errors": 0,
      "inserted": 0,
      "replaced": 1,
      "skipped": 0,
      "unchanged": 0
    }

**Delete a single account record:**

User's can only delete their account record.

::

    curl -v -X DELETE "http://127.0.0.1:8081/v1/account/776236bc-5ca9-4083-bb20-b12043ec87de" -H "content-type: application/json" -H "api-key: d615166b1818ef41b925c40b5483474522bffc94" -H "username: samjones"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "deleted": 1,
      "errors": 0,
      "inserted": 0,
      "replaced": 0,
      "skipped": 0,
      "unchanged": 0
    }

**Delete all account records (admin only):**

**Careful:** This deletes all account records (except admin). The ``deleted``
field in the response will contain how many records were deleted.

::

    curl -v -X DELETE "http://127.0.0.1:8081/v1/accounts" -H "content-type: application/json" -H "api-key: f2fe92411648dab36532d4256a5d36be0b219d53" -H "username: admin"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "deleted": 4,
      "errors": 0,
      "inserted": 0,
      "replaced": 0,
      "skipped": 0,
      "unchanged": 0
    }

**Reset an account API key:**

Ensure your service endpoint is running as the PyWebhooks server will perform a
``GET`` against your endpoint with the new ``api_key`` in the querystring as:

::

    GET /account/alternate/endpoint?api_key=768a8c2530956c0f2ac52faee785cadf3f5bc68d

**Note:** A ``GET`` is used on the endpoint like the echo challenge since ``POST`` is
used by incoming webhooks.

::

    curl -v -X POST "http://127.0.0.1:8081/v1/account/reset/apikey" -H "content-type: application/json" -H "username: sarahfranks"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "Message": "New key sent to endpoint"
    }

**Reset an account secret key:**

Ensure your service endpoint is running as the PyWebhooks server will perform a
``GET`` against your endpoint with the new ``secret_key`` in the querystring as:

::

    GET /account/alternate/endpoint?secret_key=0d7929e61c97e10a70dd71cb839853bcd4f9e230

**Note:** A ``GET`` is used on the endpoint like the echo challenge since ``POST`` is
used by incoming webhooks.

::

    curl -v -X POST "http://127.0.0.1:8081/v1/account/reset/secretkey" -H "content-type: application/json" -H "username: johndoe" -H "api-key: 9241a57a6b4d785d7acb0fe9d99f7983f4d7584b"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "Message": "New key sent to endpoint"
    }

Webhook Actions
^^^^^^^^^^^^^^^

The real essence of PyWebhooks is ultimately registering a webhook with the system
and then having users/services subscribe to those webhooks and posting the data
to your endpoint.

**Creating a new webhook registration:**

In this example we will register the following webhook from the ``johndoe``
account.

::

    {
        "items": [
            {
                "item1": 1
            },
            {
                "item2": 2
            }
        ],
        "message": "hello world"
    }

There are a few things you need to include in the JSON payload.

``description`` is a user comsumable description of what your webhook is about
``event_data`` is the actual JSON payload that will be delivered to each
subscribed user/service of this webhook when you trigger it
``event`` is a header field that is a short description of what kind of event
this is

The full payload would be something like this:

::

    {
        "description": "This is my registered webhook",
        "event_data": {
            "items": [
                {
                    "item1": 1
                },
                {
                    "item2": 2
                }
            ],
            "message": "hello world"
        },
        "event": "mywebhook.event"
    }

Create the webhook:

::

    curl -v -X POST "http://127.0.0.1:8081/v1/webhook/registration" -H "content-type: application/json" -H "username: johndoe" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97" -d '{"description": "This is my registered webhook", "event_data": {"items": [{"item1": 1}, {"item2": 2}], "message": "hello world"}, "event": "mywebhook.event"}'

**Response:**

**HTTP/1.0 201 CREATED**

::

    {
      "account_id": "d969a56d-e520-405d-a24f-497ac6923781",
      "description": "This is my registered webhook",
      "epoch": 1441166640.359496,
      "event": "mywebhook.event",
      "event_data": {
        "items": [
          {
            "item1": 1
          },
          {
            "item2": 2
          }
        ],
        "message": "hello world"
      },
      "id": "3e25a22e-6a83-4cf0-a2bf-d7617aa32551"
    }

**Delete a webhook registration:**

Deletes registration record, will also remove the records for this registration
id in the subscription table as well.

::

    curl -v -X DELETE "http://127.0.0.1:8081/v1/webhook/registration/0c296ca8-69ce-4274-b377-3010072363f9" -H "content-type: application/json" -H "username: johndoe" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "deleted": 1,
      "errors": 0,
      "inserted": 0,
      "replaced": 0,
      "skipped": 0,
      "unchanged": 0
    }

**Get all your registered webhook records:**

Lists all the calling username's registered webhooks.

This is a paginated call with ``start`` and ``limit`` params in the querystring.

**REQUIRED** ``start`` is where in the records you want to start listing (0..n)

**REQUIRED** ``limit`` is how many records to return

::

    curl -v -X GET "http://127.0.0.1:8081/v1/webhook/registration?start=0&limit=10" -H "content-type: application/json" -H "username: johndoe" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "next_start": 1,
      "registrations": [
        {
          "account_id": "fb8854ba-b7f7-4552-bc13-4d5cdbb444dd",
          "description": "This is my registered webhook",
          "epoch": 1441139002.671599,
          "event": "mywebhook.event",
          "event_data": {
            "items": [
              {
                "item1": 1
              },
              {
                "item2": 2
              }
            ],
            "message": "hello world"
          },
          "id": "4618dc47-aaf9-401e-9aa4-8fda5d59eb25"
        }
      ]
    }

**Get all registered webhook records:**

Lists all registered webhooks.

This is a paginated call with ``start`` and ``limit`` params in the querystring.

**REQUIRED** ``start`` is where in the records you want to start listing (0..n)

**REQUIRED** ``limit`` is how many records to return

::

    curl -v -X GET "http://127.0.0.1:8081/v1/webhook/registrations?start=0&limit=2" -H "content-type: application/json" -H "username: johndoe" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "next_start": 2,
      "registrations": [
        {
          "account_id": "a6903d9f-de93-4910-8d8c-06e22f434d05",
          "description": "Some description goes here",
          "epoch": 1441138315.006409,
          "event": "webhook.event.hello",
          "event_data": {
            "msg": "hello world"
          },
          "id": "ae8dc785-d4bf-4614-98a7-32dcf03314e8"
        },
        {
          "account_id": "fb8854ba-b7f7-4552-bc13-4d5cdbb444dd",
          "description": "This is my registered webhook",
          "epoch": 1441139002.671599,
          "event": "mywebhook.event",
          "event_data": {
            "items": [
              {
                "item1": 1
              },
              {
                "item2": 2
              }
            ],
            "message": "hello world"
          },
          "id": "4618dc47-aaf9-401e-9aa4-8fda5d59eb25"
        }
      ]
    }

**Delete all webhook registration records (admin only):**

**Careful:** This deletes all registration records. The ``deleted``
field in the response will contain how many records were deleted.

::

    curl -v -X DELETE "http://127.0.0.1:8081/v1/webhook/registrations" -H "content-type: application/json" -H "api-key: ba86c64c24f361ddbcfe27be187d8d3002c9f43c" -H "username: admin"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "deleted": 2,
      "errors": 0,
      "inserted": 0,
      "replaced": 0,
      "skipped": 0,
      "unchanged": 0
    }

**Update a webhook registration record:**

Only the ``description`` field can be updated on an registration.

Make sure to supply the webhook registration id as per the example.

::

    curl -v -X PATCH "http://127.0.0.1:8081/v1/webhook/registration/4618dc47-aaf9-401e-9aa4-8fda5d59eb25" -d '{"description": "New Description"}' -H "content-type: application/json" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97" -H "username: johndoe"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "deleted": 0,
      "errors": 0,
      "inserted": 0,
      "replaced": 1,
      "skipped": 0,
      "unchanged": 0
    }

Subscription Actions
^^^^^^^^^^^^^^^^^^^^

**Creating a subscription:**

Create a subscription for a registered webhook that you want to receive
notifications from when they are triggered.

::

    curl -v -X POST "http://127.0.0.1:8081/v1/webhook/subscription/ae8dc785-d4bf-4614-98a7-32dcf03314e8" -H "content-type: application/json" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97" -H "username: johndoe"


**Response:**

**HTTP/1.0 201 CREATED**

::

    {
      "account_id": "fb8854ba-b7f7-4552-bc13-4d5cdbb444dd",
      "epoch": 1441145067.959285,
      "id": "cf20c039-6355-40b9-a601-cad4e79dbe52",
      "registration_id": "ae8dc785-d4bf-4614-98a7-32dcf03314e8"
    }

**Get all your subscription records:**

Lists all the calling username's subscription records.

This is a paginated call with ``start`` and ``limit`` params in the querystring.

**REQUIRED** ``start`` is where in the records you want to start listing (0..n)

**REQUIRED** ``limit`` is how many records to return

::

    curl -v -X GET "http://127.0.0.1:8081/v1/webhook/subscription?start=0&limit=5" -H "content-type: application/json" -H "username: johndoe" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "subscriptions": [
        {
          "account_id": "fb8854ba-b7f7-4552-bc13-4d5cdbb444dd",
          "epoch": 1441144968.505692,
          "id": "9e596765-da94-46d2-9f9d-a4d7ecc374ab",
          "registration_id": "ae8dc785-d4bf-4614-98a7-32dcf03314e8"
        },
        {
          "account_id": "fb8854ba-b7f7-4552-bc13-4d5cdbb444dd",
          "epoch": 1441145067.959285,
          "id": "cf20c039-6355-40b9-a601-cad4e79dbe52",
          "registration_id": "ac18dc47-abf9-401e-8bb3-8fda5d51af48"
        }
      ]
    }

**Get all subscription records:**

Lists all subscriptions.

This is a paginated call with ``start`` and ``limit`` params in the querystring.

**REQUIRED** ``start`` is where in the records you want to start listing (0..n)

**REQUIRED** ``limit`` is how many records to return

::

    curl -v -X GET "http://127.0.0.1:8081/v1/webhook/subscriptions?start=0&limit=2" -H "content-type: application/json" -H "username: johndoe" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "next_start": 2,
      "subscriptions": [
        {
          "account_id": "fb8854ba-b7f7-4552-bc13-4d5cdbb444dd",
          "epoch": 1441144968.505692,
          "id": "9e596765-da94-46d2-9f9d-a4d7ecc374ab",
          "registration_id": "ae8dc785-d4bf-4614-98a7-32dcf03314e8"
        },
        {
          "account_id": "fb8854ba-b7f7-4552-bc13-4d5cdbb444dd",
          "epoch": 1441145067.959285,
          "id": "cf20c039-6355-40b9-a601-cad4e79dbe52",
          "registration_id": "ae8dc785-d4bf-4614-98a7-32dcf03314e8"
        }
      ]
    }

**Delete a single subscription record:**

Deletes subscription record.

::

    curl -v -X DELETE "http://127.0.0.1:8081/v1/webhook/subscription/bfbafaa0-5816-456d-9639-98023ec5dc2e" -H "content-type: application/json" -H "username: johndoe" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "deleted": 1,
      "errors": 0,
      "inserted": 0,
      "replaced": 0,
      "skipped": 0,
      "unchanged": 0
    }

**Delete all subscription records (admin only):**

**Careful:** This deletes all subscription records. The ``deleted``
field in the response will contain how many records were deleted.

::

    curl -v -X DELETE "http://127.0.0.1:8081/v1/webhook/subscriptions" -H "content-type: application/json" -H "api-key: ba86c64c24f361ddbcfe27be187d8d3002c9f43c" -H "username: admin"

**Response:**

**HTTP/1.0 200 OK**

::

    {
      "deleted": 4,
      "errors": 0,
      "inserted": 0,
      "replaced": 0,
      "skipped": 0,
      "unchanged": 0
    }

Triggered Actions
^^^^^^^^^^^^^^^^^

There are two actions that can be done:

1. Trigger a webhook

2. List all the triggered webhooks

**Trigger a webhook:**

Use a registration id to trigger the webhook (inserts a triggered record).

::

    curl -v -X POST "http://127.0.0.1:8081/v1/webhook/triggered/bfbafaa0-5816-456d-9639-98023ec5dc2e" -H "content-type: application/json" -H "api-key: ee98cb7b5da901c12bac7c263b28f7a028a5de97" -H "username: johndoe"

**Response:**

**HTTP/1.0 201 CREATED**

::

    {
      "epoch": 1441334032.467688,
      "id": "7c9cfb5c-dd9b-47cc-8579-32e06337e0f9",
      "registration_id": "bfbafaa0-5816-456d-9639-98023ec5dc2e"
    }

**Get all triggered webhooks:**

Lists all triggered records.

This is a paginated call with ``start`` and ``limit`` params in the querystring.

**REQUIRED** ``start`` is where in the records you want to start listing (0..n)

**REQUIRED** ``limit`` is how many records to return

::

    {
      "triggered_webhooks": [
        {
          "epoch": 1441333750.649395,
          "id": "fc20ee3f-2278-4d14-1058-afab5b2c1b34",
          "registration_id": "bfbafaa0-5816-456d-9639-98023ec5dc2e"
        },
        {
          "epoch": 1441333775.45855,
          "id": "abf196cf-e3cd-47d5-9458-ecc22e5e1ae3",
          "registration_id": "3279b8af-3a90-4cf1-afb8-12872849b2ac"
        },
        {
          "epoch": 1441333841.789931,
          "id": "77c674fc-1907-499e-8e52-3faa57804977",
          "registration_id": "3279b8af-3a90-4cf1-afb8-12872849b2ac"
        },
        {
          "epoch": 1441334032.467688,
          "id": "7c9cfb5c-dd9b-47cc-8579-32e06337e0f9",
          "registration_id": "3279b8af-3a90-4cf1-afb8-12872849b2ac"
        }
      ]
    }

**Response:**

**HTTP/1.0 200 OK**

License
^^^^^^^

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
