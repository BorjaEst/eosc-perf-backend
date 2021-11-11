"""Authorization module."""
import functools
import re

import requests
from authlib.integrations.flask_oauth2 import ResourceProtector, current_token
from authlib.oauth2.rfc7662 import IntrospectTokenValidator
from flask import abort, current_app


from .extensions import oauth


class MyIntrospectTokenValidator(IntrospectTokenValidator):
    def introspect_token(self, token_string):
        oauth.egi.load_server_metadata()
        url = oauth.egi.server_metadata['introspection_endpoint']
        data = {'token': token_string, 'token_type_hint': 'access_token'}
        auth = (oauth.egi.client_id, oauth.egi.client_secret)
        resp = requests.post(url, data=data, auth=auth)
        if resp.status_code != 200:
            abort(resp.status_code, resp.json())
        return resp.json()


# only bearer token is supported currently
require_oauth = ResourceProtector()
require_oauth.register_token_validator(MyIntrospectTokenValidator())


@require_oauth('eduperson_entitlement')
def is_admin():
    any_of = current_app.config['ADMIN_ENTITLEMENTS']
    entitlements = current_token['eduperson_entitlement']
    return not set(any_of).isdisjoint(entitlements)


def require_admin():
    """Decorator to enforce a administration rights."""
    def wrapper(route):
        @functools.wraps(route)
        def decorated(*args, **kwargs):
            if not is_admin():
                abort(403)
            return route(*args, **kwargs)
        return decorated
    return wrapper
