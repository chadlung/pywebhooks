import base64
import hashlib
import hmac
from http import client

from flask import Flask
from flask import request, make_response, jsonify


app = Flask(__name__)

# Adjust this as needed
SECRET_KEY = '509566acece60d5daf8699f16e4a6d3bb6aebfe1'


def verify_hmac_hash(incoming_json, secret_key, incoming_signature):
    signature = hmac.new(
        str(secret_key).encode('utf-8'),
        str(incoming_json).encode('utf-8'),
        digestmod=hashlib.sha1
    ).digest()

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

    is_signature_valid = verify_hmac_hash(
        request.json,
        SECRET_KEY,
        base64.urlsafe_b64decode(request.headers['pywebhooks-signature'])
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
