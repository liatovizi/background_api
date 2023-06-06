from flask_httpauth import HTTPTokenAuth, MultiAuth
from flask import g, request
from natapp.libs.naterrors import Errors
from natapp.response import *
import logging
from datetime import datetime
from natapp.decorator import fmt_json_response
from natapp.nat.db import auth as natdb
from natapp.libs import natbgservice as bgservicelib
from natapp.libs.natusers import get_user_access_rights
import re

app_auth = HTTPTokenAuth(scheme='Bearer')

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

    instance = natdb.get_instance_by_token(token)

    if instance is None:
        return None

    return instance


@app_auth.verify_token
def verify_user_token(token):
    instance = None

    instance = get_token(token)

    if instance is None:
        return False

    g.current_instance = instance.instance_id
    g.current_instance_status = instance.status
    manual_update_last_auth_call()

    return True


@app_auth.error_handler
@fmt_json_response
def unauthorized(*args):
    return RESP_ERR, Errors.EGEN_unauth_E001


# get session instance id
def get_instanceid():
    return g.current_instance


# set session instance id
def set_instanceid(instance_id):
    g.current_instance = instance_id


# get session instance status
def get_instancestatus():
    return g.current_instance_status


def manual_update_last_auth_call():
    natdb.update_instance_last_authorized_call(get_instanceid())
