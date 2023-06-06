from flask_httpauth import HTTPTokenAuth, MultiAuth
from flask import g, request
from natapp.libs.naterrors import Errors
from natapp.response import *
import logging
from datetime import datetime
from natapp.decorator import fmt_json_response
from natapp.users.db import login as users_login
from natapp.libs import natbgservice as bgservicelib
from natapp.libs.natusers import get_user_access_rights
import re

token_auth = HTTPTokenAuth(scheme='Bearer')
bgservice_auth = HTTPTokenAuth(scheme='Bearer')
multi_auth = MultiAuth(token_auth)

logger = logging.getLogger('flask.app')

authorizations = {
    'tokenAuth': {
        'type': 'http',
        'scheme': 'bearer',
    }
}


def get_token(token):
    if not token:
        return None


#    try:
#        scheme, token = auth_in.split(None, 1)
#    except (KeyError, ValueError):
#        # Malformed or missing headers
#        logger.warning("invalid authentication received")
#        return None
#    if scheme != 'token':
#        logger.warning(f"invalid authentication scheme received: {scheme}")
#        return None

    if re.search('^[A-Z0-9a-z_.-]*$', token) is None:
        users_login.drop_token(str(token))
        return None

    token_rec = users_login.get_tokens(token)

    if token_rec is None:
        return None

    if token_rec.valid_to <= datetime.utcnow():
        return None

    return token_rec


@token_auth.verify_token
def verify_user_token(token):
    token_rec = None

    token_rec = get_token(token)

    if token_rec is None:
        return False

    if token_rec.user_id == bgservicelib.bgservice_user_id:
        return False

    g.current_user = token_rec.user_id
    g.current_user_access_rights = get_user_access_rights(get_userid())

    return True


@token_auth.error_handler
@fmt_json_response
def unauthorized(*args):
    return RESP_ERR, Errors.EGEN_unauth_E001


@bgservice_auth.verify_token
def verify_bgservice_token(token):
    token_rec = None

    token_rec = get_token(token)

    if token_rec is None:
        return False

    if token_rec.user_id != bgservicelib.bgservice_user_id:
        return False

    g.current_user = token_rec.user_id
    g.current_user_access_rights = get_user_access_rights(get_userid())

    return True


@bgservice_auth.error_handler
@fmt_json_response
def unauthorized(*args):
    return RESP_ERR, Errors.EGEN_unauth_E001


# get session user id
def get_userid():
    return g.current_user


# set session user id
def set_userid(user_id):
    g.current_user = user_id


# get session user rights
def get_userrights():
    return g.current_user_access_rights


def manual_update_last_auth_call():
    users_login.update_user_last_authorized_call(get_userid())
