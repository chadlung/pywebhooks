# Standard lib imports
from time import time
import uuid

# Third-party imports
import rethinkdb as rethink

# Project-level imports
from pywebhooks.utils.rethinkdb_helper import get_connection


class Interactions(object):
    """
    Handles basic table interactions
    """

    @staticmethod
    def list(table_name, start, limit, order_by='epoch', filters=None):
        """
        Gets a list of records, meant for pagination.
        """
        if not filters:
            filters = {}

        with get_connection() as conn:
            return rethink.table(table_name)\
                .filter(filters).order_by(order_by) \
                .slice(start, limit).run(conn)

    @staticmethod
    def list_all(table_name, order_by='epoch', filters=None):
        """
        Gets a full list of records - no pagination.
        """
        if not filters:
            filters = {}

        with get_connection() as conn:
            return list(rethink.table(table_name)
                        .order_by(order_by).filter(filters).run(conn))

    @staticmethod
    def query(table_name, order_by='epoch', filters=None):
        """
        Query for record(s)
        """
        if not filters:
            filters = {}

        with get_connection() as conn:
            return rethink.table(table_name)\
                .order_by(order_by).filter(filters).run(conn)

    @staticmethod
    def get(table_name, record_id):
        """
        Get a single record based on id.
        """
        with get_connection() as conn:
            return rethink.table(table_name).get(record_id).run(conn)

    @staticmethod
    def insert(table_name, **kwargs):
        """
        Inserts a new record. id and epoch are common to all records.
        """
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())

        kwargs['epoch'] = time()

        with get_connection() as conn:
            rethink.table(table_name).insert(kwargs).run(conn)
        return kwargs

    @staticmethod
    def delete_all(table_name):
        """
        Deletes all records in a specified table
        """
        with get_connection() as conn:
            return rethink.table(table_name).delete().run(conn)

    @staticmethod
    def delete(table_name, record_id):
        """
        Deletes a single record in a specified table
        """
        with get_connection() as conn:
            return rethink.table(table_name).get(record_id).delete().run(conn)

    @staticmethod
    def delete_specific(table_name, filters=None):
        """
        Deletes all records in a table matching the filter
        """
        if not filters:
            filters = {}

        with get_connection() as conn:
            return rethink.table(table_name).filter(filters).delete().run(conn)

    @staticmethod
    def update(table_name, record_id=None, filters=None, updates=None):
        """
        Perform an update on one more fields
        """
        if not filters:
            filters = {}
        if not updates:
            updates = {}

        with get_connection() as conn:
            if record_id:
                return rethink.table(table_name).get(record_id)\
                    .update(updates).run(conn)
            else:
                return rethink.table(table_name).filter(filters)\
                    .update(updates).run(conn)
