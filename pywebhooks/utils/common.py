# Standard lib imports
import json
import hashlib
import hmac
import os

# Third-party imports
# None

# Project-level imports
# None


def generate_key():
    return str(hashlib.sha1(os.urandom(128)).hexdigest())


def create_signature(secret_key, json_data, digestmod=hashlib.sha1):
    return hmac.new(
        str(secret_key).encode('utf-8'),
        str(json.dumps(json_data)).encode('utf-8'),
        digestmod=digestmod
    ).hexdigest()
