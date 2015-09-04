# Standard lib imports
from http import client

# Third-party imports
from flask import make_response, jsonify

# Project-level imports
from pywebhooks.database.rethinkdb.interactions import Interactions


def paginate(request, table_name, resource_name, filters=None):

        limit = int(request.args.get('limit'))
        start = int(request.args.get('start'))

        if not filters:
            filters = {}

        end = start + limit

        returned_records = Interactions.list(
            table_name, start, end, 'epoch', filters=filters)

        records = []

        for item in returned_records:
            records.append(item)

        if len(returned_records) == 0:
            return make_response('', client.NO_CONTENT)

        if len(returned_records) < limit:
            return_json = {
                resource_name: records
            }
        else:
            return_json = {
                'next_start': end,
                resource_name: records
            }

        return make_response(jsonify(return_json), client.OK)
