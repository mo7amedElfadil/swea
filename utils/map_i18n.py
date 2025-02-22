'''This module contains a decorator that normalizes service response base on locale'''
from functools import wraps
from typing import Any

import flask
import werkzeug
import werkzeug.wrappers


def normailze_i18n(f):
    '''Decorator that converts a return value from a view,
    into a dict filled with data based on the locale
    '''
    def dfs(locale: str, val: Any) -> Any:
        '''Helper function to traverse nested dictionaries'''
        if not isinstance(val, (dict,list)):
            return val
        elif isinstance(val, dict):
            if locale in val:
                return val[locale]
            for k, v in val.items():
                val[k] = dfs(locale, v)
        elif isinstance(val, list):
            for i, v in enumerate(val):
                val[i] = dfs(locale, v)
        return val

    @wraps(f)
    def view_method(*args, **kwargs):
        response_val = f(*args, **kwargs)

        if isinstance(response_val, werkzeug.wrappers.Response):
            return response_val

        if isinstance(response_val, flask.Response):
            return response_val

        if isinstance(response_val, dict):
            response_val = dfs(response_val.get('locale'), response_val)

        return response_val

    return view_method
