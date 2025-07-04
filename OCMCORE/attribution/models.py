from django.db import connections
import pandas as pd

class StoredProcedureCaller:
    """
    Helper to call a stored procedure by name and arguments, returning results as a list of dicts or a pandas DataFrame.

    Usage:
        from core.models import StoredProcedureCaller
        sp = StoredProcedureCaller(db_alias='analytics')  # or 'default', etc.
        results = sp.call('my_stored_procedure', [arg1, arg2, ...])
        # results is a list of dicts, one per row

        # To get a pandas DataFrame:
        df = sp.as_dataframe('my_stored_procedure', [arg1, arg2, ...])
    """
    def __init__(self, db_alias='default'):
        self.db_alias = db_alias

    def call(self, proc_name, args=None):
        args = args or []
        with connections[self.db_alias].cursor() as cursor:
            cursor.callproc(proc_name, args)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            results = [dict(zip(columns, row)) for row in cursor.fetchall()] if columns else []
        return results

    def as_dataframe(self, proc_name, args=None):
        args = args or []
        with connections[self.db_alias].cursor() as cursor:
            cursor.callproc(proc_name, args)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall() if columns else []
        return pd.DataFrame(rows, columns=columns) if columns else pd.DataFrame() 