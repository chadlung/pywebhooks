from __future__ import print_function

from pywebhooks.util.request import http_request
from pywebhooks import CELERY


# This is just a temporary sanity check
@CELERY.task(serializer="json")
def request_version(msg):
    print('log_message {}'.format(msg))
    response = http_request(url='http://localhost:8080',
                                http_verb='GET')
    print(response.content)
