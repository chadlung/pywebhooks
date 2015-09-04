# Standard lib imports
import base64
import hashlib
import hmac
import os

# Third-party imports
# None

# Project-level imports
# None


def generate_key():
    return str(hashlib.sha1(os.urandom(128)).hexdigest())


def create_signature(secret_key, json_data, digestmod=hashlib.sha1,
                     base64_encode=True):
        signature = hmac.new(
            str(secret_key).encode('utf-8'),
            str(json_data).encode('utf-8'),
            digestmod=digestmod
        ).digest()

        if base64_encode:
            return base64.urlsafe_b64encode(signature)
        else:
            return signature
