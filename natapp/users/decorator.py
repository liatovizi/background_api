from functools import wraps

from flask import request, jsonify, current_app

from natapp.libs.naterrors import Errors
from natapp.response import *
from natapp import db
import traceback
from natapp.users.db import login as users_login
from natapp.users import auth

from natapp.decorator import fmt_response


def update_last_auth_call(func):
    @wraps(func)
    def call_wrap(*args, **kwargs):
        users_login.update_user_last_authorized_call(auth.get_userid())
        #        db.session.commit()
        result = func(*args, **kwargs)
        return result

    return call_wrap


def require_right(*inargs):
    def wrapper(func):
        @wraps(func)
        def call_wrap(*args, **kwargs):
            user_access_rights = auth.get_userrights()
            for i in inargs:
                if isinstance(i, list):
                    istrue = False
                    for j in i:
                        if j in user_access_rights:
                            istrue = True
                            break
                    if not istrue:
                        return fmt_response({}, errcode=Errors.EGEN_unauth_E001), 401
                else:
                    if i not in user_access_rights:
                        return fmt_response({}, errcode=Errors.EGEN_unauth_E001), 401
            result = func(*args, **kwargs)
            return result

        return call_wrap

    return wrapper
