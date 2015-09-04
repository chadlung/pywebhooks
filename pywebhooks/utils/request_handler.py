# Standard lib imports
import json

# Third party imports
import requests

# Project level imports
# None


# Suppress the insecure request warning
# https://urllib3.readthedocs.org/en/
# latest/security.html#insecurerequestwarning
requests.packages.urllib3.disable_warnings()


class RequestHandler(object):

    def __init__(self, verify_ssl=False, request_timeout=15.0):

        self.verify_ssl = verify_ssl
        self.request_timeout = request_timeout
        self._session = requests.Session()
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}

    def get(self, url, params=None, api_key=None, username=None):
        return self._request(url, params=params, api_key=api_key,
                             username=username)

    def post(self, url, json_payload='{}', api_key=None, username=None,
             event=None, signature=None):
        return self._request(url, json_payload, http_verb='POST',
                             api_key=api_key, username=username,
                             event=event, signature=signature)

    def patch(self, url, json_payload='{}', api_key=None, username=None):
        return self._request(url, json_payload, http_verb='PATCH',
                             api_key=api_key, username=username)

    def put(self, url, json_payload='{}', api_key=None, username=None):
        return self._request(url, json_payload, http_verb='PUT',
                             api_key=api_key, username=username)

    def delete(self, url, params=None, api_key=None, username=None):
        return self._request(url, params=params, http_verb='DELETE',
                             api_key=api_key, username=username)

    def _request(self, url, json_payload='{}', http_verb='GET', params=None,
                 api_key=None, username=None, event=None, signature=None):

        json_payload = json.dumps(json_payload)

        if api_key:
            self.headers['api-key'] = api_key
        if username:
            self.headers['username'] = username
        if event:
            self.headers['event'] = event
        if signature:
            self.headers['pywebhooks-signature'] = signature

        # try:
        if http_verb == "PUT":
            req = self._session.put(
                url=url,
                verify=self.verify_ssl,
                headers=self.headers,
                timeout=self.request_timeout,
                data=json_payload)
        elif http_verb == 'POST':
            req = self._session.post(
                url=url,
                verify=self.verify_ssl,
                headers=self.headers,
                timeout=self.request_timeout,
                data=json_payload)
        elif http_verb == 'PATCH':
            req = self._session.patch(
                url=url,
                verify=self.verify_ssl,
                headers=self.headers,
                timeout=self.request_timeout,
                data=json_payload)
        elif http_verb == 'DELETE':
            req = self._session.delete(
                url=url,
                verify=self.verify_ssl,
                headers=self.headers,
                timeout=self.request_timeout,
                params=params)
        else:  # Default to GET
            req = self._session.get(
                url=url,
                verify=self.verify_ssl,
                headers=self.headers,
                timeout=self.request_timeout,
                params=params)

        return req.json(), req.status_code
