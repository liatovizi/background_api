import json
import re
import os
import random
import string
import time
import hashlib
from datetime import timedelta, datetime
from functools import wraps
import secrets
import jwt

from natapp.response import *
from natapp.blueprint import RegisteringBlueprint

from natapp.libs.naterrors import Errors
from natapp import db
from .auth import multi_auth, bgservice_auth, get_userid
from .decorator import update_last_auth_call, require_right
from natapp.libs.natusers import AccessRights, get_user_access_rights
from natapp.decorator import fmt_json_response, autocommit, req_method_decorator, fmt_json_response_dict

from natapp.users.db import login as users_login
from natapp.users.db import user as users_user
from natapp.users import utils as users_utils
import natapp.libs.natemailsender as natemailsender
import natapp.libs.natutility as nat_utils
import natapp.libs.natusers as natusers
#from flask_restplus import Resource, fields, reqparse
from flask_restx import Resource, fields, reqparse
from natapp.namespace import RegisteringNamespace as Namespace

user = RegisteringBlueprint('user', __name__, url_prefix="/tggapp/api/v1.0")
api = Namespace('users', description='Natapp user management related operations')


@user.after_request
def apply_caching(response):
    r = request.headers["Origin"] if "Origin" in request.headers else "*"
    response.headers["Access-Control-Allow-Origin"] = r
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "content-type, authorization, doctype"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS, GET, HEAD, PUT"
    return response


# -----------------------------
# --- SESSION HANDLING PART ---
# -----------------------------

from flask import g, request, jsonify, make_response


def get_userrole():
    return g.userrole


def set_userrole(userrole):
    g.userrole = userrole


@api.route('private/refresh')
class RefreshToken(Resource):
    @api.requestdecorator('RefreshTokenGet',
                          parserparams=[('refresh_token', {
                              'help': 'refresh token',
                              'location': 'args',
                              'required': True
                          })],
                          response_200={
                              'access_token': fields.String(example="accesstokenstring",
                                                            description="user access token"),
                              'refresh_token': fields.String(example="refreshtokenstring",
                                                             description="user refresh token"),
                              'expires_in': fields.Integer(example=10000, description="token validity in seconds")
                          },
                          errors=[Errors.EREG_badusr_E002, Errors.EGEN_lockedout_E001, Errors.EGEN_unauth_E001])
    @fmt_json_response_dict
    @autocommit
    def get(self):
        """get new access token using the refresh token"""
        return self.common(request.args['refresh_token'])

    @api.requestdecorator('RefreshTokenPost',
                          jsonfields={
                              'refresh_token':
                              fields.String(example="refreshtokenxyz", description="refresh token", required=True)
                          },
                          response_200={
                              'access_token': fields.String(example="accesstokenstring",
                                                            description="user access token"),
                              'refresh_token': fields.String(example="refreshtokenstring",
                                                             description="user refresh token"),
                              'expires_in': fields.Integer(example=10000, description="token validity in seconds")
                          },
                          errors=[Errors.EGEN_invchars_E001, Errors.EGEN_tokenref_E001, Errors.ERFS_old_token_E001])
    @fmt_json_response_dict
    @autocommit
    def post(self):
        """get new access token using the refresh token"""
        return self.common(api.payload['refresh_token'])

    def common(self, refresh_token):
        if re.search('^[A-Z0-9a-z]*$', refresh_token) is None:
            return RESP_ERR, Errors.EGEN_invchars_E001

        c = users_login.get_renew_tokens(refresh_token)
        if not c:
            return RESP_ERR, Errors.EGEN_tokenref_E001

        # Rejecting the refresh token if the user was inactive for more than the configured interval.
        last_authorized_call = users_login.get_user_last_authorized_call(c[0]['user_id'])
        if last_authorized_call + timedelta(seconds=users_login.REFRESH_MAX_USER_INACTIVITY) < datetime.now():
            users_login.drop_token(str(c[0]["token"]))
            return RESP_ERR, Errors.ERFS_old_token_E001

        # Updating the last authorized call timestamp.
        users_login.update_user_last_authorized_call(c[0]['user_id'])

        u = users_user.get_users_by_user_id(c[0]['user_id'])

        #       new_access_token = f'{u[0]["privileges"]}-' + (''.join(
        #            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(25)))
        new_access_token = jwt.encode(
            {
                'privileges': u[0]["privileges"],
                'sid': ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(30))
            },
            'secret',
            algorithm='HS256')
        new_refresh_token = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(30))
        new_exp = datetime.utcnow() + timedelta(seconds=users_login.ACCESS_TOKEN_VALIDITY)
        new_renew = datetime.utcnow() + timedelta(seconds=users_login.REFRESH_TOKEN_VALIDITY)
        _a = {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'expires_in': users_login.ACCESS_TOKEN_VALIDITY
        }
        users_login.renew_token(new_access_token, new_refresh_token, new_exp, new_renew, refresh_token)
        return RESP_OK, _a


# --------------------------
# -------- LOGIN PART ------
# --------------------------
#@user.route('/public/login', methods=['POST', 'GET'])
#@user.route('/admin/login', methods=['POST', 'GET'])
#@fmt_json_response
#@req_method_decorator("username", "password")
@api.route('public/login')
@api.route('admin/login')
class Login(Resource):
    @api.requestdecorator('Login',
                          jsonfields={
                              'username':
                              fields.String(example="user",
                                            min_length=4,
                                            description="selected username",
                                            required=True),
                              'password':
                              fields.String(example="password",
                                            description="selected password",
                                            min_length=2,
                                            required=True)
                          },
                          response_200={
                              'access_token': fields.String(example="sometokenstring", description="user access token"),
                              'refresh_token': fields.String(example="sometokenstring2",
                                                             description="user refresh token"),
                              'expires_in': fields.Integer(example=10000, description="token validity in seconds")
                          },
                          errors=[Errors.EREG_badusr_E002, Errors.EGEN_lockedout_E001, Errors.EGEN_unauth_E001])
    @fmt_json_response_dict
    @autocommit
    def post(self):
        """login to the application as user/admin"""
        username = api.payload['username']
        password = api.payload['password']
        if re.search('^[A-Z0-9a-z.!@#\+\$\?\_\-]*$', username) is None \
                or re.search('^[A-Z0-9a-z.!@#\+\$\?\_\-\%]*$', password) is None\
                or len(username) == 0:
            return RESP_ERR, Errors.EREG_badusr_E002

        login_data = users_login.get_user(username)

        if not login_data:
            # Try to interpret the username as email address.
            login_data = users_login.get_user_by_email(username)

        if login_data and users_utils.check_password(password, login_data['password']):
            u = users_user.get_users_by_user_id(login_data['user_id'])
            if len(u) != 1 or u[0]['locked'] != 0:
                return RESP_ERR, Errors.EGEN_lockedout_E001

            user_id = str(login_data['user_id'])

            _x_fwd_to = "N/A"
            _cf_conn_ip = "N/A"
            try:
                _x_fwd_to = request.headers.get('X-Forwarded-For')
                _cf_conn_ip = request.headers.get('CF-Connecting-IP')
            except:
                pass
            #Check necessary rights if user try to login to admin panel

    #        if '/admin' in request.path:
    #           #if xchusers.get_user_privilegesmask(user_id) <= xchusers.AccessRights.NORMAL_USER:
    #          if pwd != "admin":
    #             user.logger.error(
    #            f'Forbidded user login for admin panel: user_id={user_id} addr={request.remote_addr} XFWD:{_x_fwd_to} CFIP:{_cf_conn_ip}'
    #       )
    #      return RESP_ERR, Errors.EGEN_lockedout_E001

    #token = f'{u[0]["privileges"]}-' + (''.join(
    #    secrets.choice(string.ascii_lowercase + string.digits) for _ in range(25)))
            token = jwt.encode(
                {
                    'privileges': u[0]['privileges'],
                    'sid': ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(30))
                },
                'secret',
                algorithm='HS256')
            renew = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(30))
            exp = datetime.utcnow() + timedelta(seconds=users_login.ACCESS_TOKEN_VALIDITY)
            renewable = datetime.utcnow() + timedelta(seconds=users_login.REFRESH_TOKEN_VALIDITY)
            result = {'access_token': token, 'refresh_token': renew, 'expires_in': users_login.ACCESS_TOKEN_VALIDITY}
            users_login.add_token(user_id, token, renew, exp, renewable)
            user.logger.debug(
                f'User login: user_id={user_id}, token={token}, renew={renew} addr={request.remote_addr} XFWD:{_x_fwd_to} CFIP:{_cf_conn_ip}'
            )
            users_login.update_data(user_id, request.remote_addr)
            users_login.update_user_last_authorized_call(user_id)
            return RESP_OK, result

        return RESP_ERR, Errors.EGEN_unauth_E001


#@req_method_decorator("username", "password")
@api.route('private/logout')
class Logout(Resource):
    @api.requestdecorator('Logout',
                          jsonfields={
                              'access_token':
                              fields.String(example="accesstokenxyz",
                                            description="access token (optional, 1 required)"),
                              'refresh_token':
                              fields.String(example="refreshtokenxyz",
                                            description="refresh token (optional, 1 required")
                          },
                          response_200={},
                          errors=[Errors.EGEN_badreq_E001, Errors.EGEN_tokenref_E001])
    @fmt_json_response_dict
    @autocommit
    def post(self):
        """logout from application"""
        access_token = None
        refresh_token = None

        if 'access_token' in api.payload:
            access_token = api.payload['access_token']

        if 'refresh_token' in api.payload:
            refresh_token = api.payload['refresh_token']

        if access_token != None and refresh_token != None:
            return RESP_ERR, Errors.EGEN_badreq_E001

        if access_token:
            token_rec = users_login.get_tokens(access_token)
            if token_rec is None:
                return RESP_ERR, Errors.EGEN_tokenref_E001
            users_login.drop_token(str(token_rec.token))
            return RESP_OK, {}
        elif refresh_token:
            c = users_login.get_renew_tokens(refresh_token)
            if not c:
                return RESP_ERR, Errors.EGEN_tokenref_E001
            users_login.drop_token(str(c[0]["token"]))
            return RESP_OK, {}
        return RESP_ERR, Errors.EGEN_badreq_E001


@api.route('private/changepassword')
class ChangePassword(Resource):
    @api.doc(security=['tokenAuth'])
    @multi_auth.login_required
    @require_right(AccessRights.NORMAL_USER)
    @api.requestdecorator('ChangePassword',
                          jsonfields={
                              'password':
                              fields.String(example="Currentpassword123", description="current password",
                                            required=True),
                              'new_password':
                              fields.String(example="newpasswOrd123", description="new password", required=True)
                          },
                          response_200={},
                          errors=[Errors.EGEN_badreq_E001, Errors.EGEN_tokenref_E001])
    @fmt_json_response_dict
    @update_last_auth_call
    @autocommit
    def post(self):
        """change password"""

        password = api.payload['password']
        new_password = api.payload['new_password']

        login_datas = users_user.get_logins_by_userid(get_userid())
        if not login_datas or login_datas == []:
            # user not found in the db
            return RESP_ERR, Errors.EGEN_badreq_E001

        if users_utils.check_password(password, login_datas[0]['password']):
            errval, retvalue = users_utils.change_password(user_id=get_userid(), password=new_password)
            if errval != "ok":
                return RESP_ERR, retvalue
            return RESP_OK, {}

        return RESP_ERR, Errors.EGEN_unauth_E001


@api.route('public/register')
class RegisterUser(Resource):
    @fmt_json_response_dict
    @autocommit
    @api.requestdecorator(
        'RegisterUser',
        jsonfields={
            'username': fields.String(example="user", description="selected username", required=True),
            'password': fields.String(example="password", description="selected password", required=True),
            'email': fields.String(example="john@doe.com", description="email address", required=True),
            'lang': fields.String(example="hu", enum=["en", "hu"], description="preferred language"),
            'newsletter': fields.Integer(min=0, max=1, example=0, description="subscribe to newsletter")
        },
        response_201={'uid': fields.String(example="112", description="registered user id")},
        errors=[
            Errors.EGEN_badreq_E001, Errors.EREG_badusr_E001, Errors.EREG_badusr_E002, Errors.EREG_badpwd_E001,
            Errors.EREG_invemail_E001, Errors.EREG_badusr_E005, Errors.EREG_badusr_E003, Errors.EREG_badusr_E006,
            Errors.EREG_badusr_E004, Errors.EGEN_dbresp_E001
        ])
    def post(self):
        """register a new user"""

        if user.config['DISABLE_REGISTRATION']:
            return RESP_ERR, Errors.EGEN_unauth_E001

        _lang = request.accept_languages.best_match(user.config['SUPPORTED_LANGUAGES'])
        if not _lang:
            _lang = 'hu'

        username = api.payload['username']
        password = api.payload['password']
        email = api.payload['email']
        newsletter = api.payload['newsletter'] if 'newsletter' in api.payload else 0

        # TODO: only allow existing users to 'invite'(register) a new user
        if 'lang' in api.payload:
            if (api.payload['lang'] == 'hu'):
                _lang = "hu"
            elif (api.payload['lang'] == "en"):
                _lang = "en"
            else:
                user.logger.warning("Invalid preferred language!!")

        errval, retvalue = users_utils.regiser_new_user(username=username,
                                                        password=password,
                                                        email=email,
                                                        newsletter=newsletter,
                                                        lang=_lang)

        if errval != "ok":
            return RESP_ERR, retvalue
        newuser = retvalue
        _params = {
            'recipient': email,
            'customer_id': newuser.user_id,
            'verifyaccount_url': user.config['VERIFYACCOUNT_URL'],
            'token': newuser.validity_token
        }
        ret = natemailsender.email_sender(db.session, 'verify_email', _params)
        if ret != None:
            return RESP_ERR, ret

        users_user.set_email_verify_sent(newuser.user_id)

        user.logger.debug(
            f'New user: user_id={newuser.user_id}, email={email}, user_name={username}, verify_token={newuser.validity_token}'
        )

        return RESP_OK_201, {'uid': str(newuser.user_id)}


@api.route('public/verifyaccount')
class VerifyAccount(Resource):
    @api.requestdecorator('VerifyAccount',
                          parserparams=[('token', {
                              'help': 'user verification token received with the registration email',
                              'location': 'args'
                          })],
                          response_200={},
                          errors=[Errors.EVRF_missing_E001, Errors.EVRF_missing_E002])
    @fmt_json_response_dict
    @autocommit
    def get(self):
        """verify account registration"""
        if not 'token' in request.args:
            return RESP_ERR, Errors.EVRF_missing_E001
        token = request.args['token']
        if len(str(token)) != 29 or not re.match(r'^[0-9abcdefxyzk\-]+$', str(token)):
            return RESP_ERR, Errors.EVRF_missing_E002

        c = users_user.get_locked_users_by_validity_token(token)
        if not c:
            return RESP_ERR, Errors.EVRF_missing_E002
        user_id = str(c[0]['user_id'])

        user.logger.debug(f'Account verifying: user_id={user_id}')
        c = users_user.validate_user(user_id, token,
                                     natusers.AccessRights.PRIVILEGE_MASKS[natusers.AccessRights.NORMAL_USER])
        user.logger.debug(f'Account verified: user_id={user_id}')

        return RESP_OK, {}


@api.route('public/forgotpassword')
class ForgotPassword(Resource):
    @api.requestdecorator('ForgotPassword',
                          jsonfields={
                              'email': fields.String(example="john@doe.com", description="email address",
                                                     required=True),
                          },
                          response_200={},
                          errors=[Errors.EGEN_dbresp_E001])
    @fmt_json_response_dict
    @autocommit
    def post(self):
        """request new password with email address"""

        if user.config['DISABLE_FORGOTPASSWORD']:
            return RESP_ERR, Errors.EGEN_unauth_E001

        email = api.payload["email"]
        c = users_user.get_users_by_email(email)
        if c == None:
            return RESP_OK, {}

        if c:
            _user = c[0]
            if _user['locked'] == 0:
                email_resetpwd_sent = _user['email_resetpwd_sent']
                if email_resetpwd_sent is None or datetime.now() - timedelta(seconds=24 * 60 *
                                                                             60) > email_resetpwd_sent:
                    s = "abcdef1234567890-xyzk"
                    reset_pwd_token = ''.join(secrets.choice(s) for x in range(29))
                    users_user.set_reset_pwd_token(_user['user_id'], reset_pwd_token)

                    # Send pwdreset_email email
                    _params = {
                        'recipient': email,
                        'customer_id': _user["user_id"],
                        'pwreset_url_base': user.config['PWRESET_URL_BASE'],
                        'token': reset_pwd_token
                    }
                    ret = natemailsender.email_sender(db.session, 'pwdreset_email', _params)
                    if ret != None:
                        return RESP_ERR, ret

                    user.logger.debug(f'User forgotpassword: user_id={_user["user_id"]}, token={reset_pwd_token}')
                else:
                    user.logger.error(
                        f'User forgotpassword: More than one attempt a day to reset password - user_id={_user["user_id"]}'
                    )
            else:
                user.logger.error(f'User locked: user_id={_user["user_id"]}')
        else:
            user.logger.error(f'User forgotpassword: email {email} not exists in Users table')
        return RESP_OK, {}


@api.route('public/resetpassword')
class ResetPassword(Resource):
    @api.requestdecorator('ResetPassword',
                          jsonfields={
                              "token":
                              fields.String(example="token_value", description="password reset token", required=True),
                              "password":
                              fields.String(description="new password", required=True)
                          },
                          errors=[
                              Errors.ERSTPWD_invalid_E002, Errors.EREG_badpwd_E001, Errors.EGEN_dbresp_E001,
                              Errors.ERSTPWD_missing_E001, Errors.ERSTPWD_old_token_E003
                          ])
    @fmt_json_response_dict
    @autocommit
    def post(self):
        """resets a users's password"""
        reset_pwd_token = api.payload["token"]
        password = api.payload["password"]

        if len(reset_pwd_token) != 29 or not re.match(r'^[0-9abcdefxyzk\-]+$', reset_pwd_token):
            return RESP_ERR, Errors.ERSTPWD_invalid_E002

        if not nat_utils.check_password_format(password):
            return RESP_ERR, Errors.EREG_badpwd_E001

        c = users_user.get_users_by_reset_pwd_token(reset_pwd_token)
        if c == None:
            return RESP_ERR, Errors.EGEN_dbresp_E001
        if not c:
            return RESP_ERR, Errors.ERSTPWD_missing_E001
        user_id = str(c[0]['user_id'])
        email_resetpwd_sent = c[0]['email_resetpwd_sent']
        if timedelta(seconds=24 * 60 * 60) < datetime.now() - email_resetpwd_sent:
            return RESP_ERR, Errors.ERSTPWD_old_token_E003

        c = users_user.reset_password(user_id, users_utils.hash_password(password))

        return RESP_OK_201, {}


# ------------------------------------------------------
# ---- FUNCTIONAL API example with json decorator ------
# ------------------------------------------------------


@api.route('private/setuserlanguage')
class SetLanguage(Resource):
    @multi_auth.login_required
    @update_last_auth_call
    @api.requestdecorator('SetUserLanguage',
                          jsonfields={
                              'lang':
                              fields.String(example="hu",
                                            description="selected language",
                                            enum=["hu", "en"],
                                            required=True)
                          },
                          response_200={'lang': fields.String(example="hu", enum=["en", "hu"])},
                          errors=[Errors.SETLANG_error_001])
    @fmt_json_response_dict
    @autocommit
    def post(self, language):
        """Set the user's preferred language"""
        _lang = language
        if _lang not in user.config['SUPPORTED_LANGUAGES']:
            return RESP_ERR, Errors.SETLANG_error_001

        users_user.set_user_preferred_language(get_userid(), _lang)
        return RESP_OK, {'lang': _lang}


@api.route('private/getuserlanguage')
class GetLanguage(Resource):
    @api.doc(security=['tokenAuth'])
    @multi_auth.login_required
    @api.requestdecorator('GetUserLanguageGet', response_200={'lang': fields.String(example="hu", enum=["en", "hu"])})
    @update_last_auth_call
    @fmt_json_response_dict
    def get(self):
        """query current preferred language"""
        _lang = users_user.get_preferred_language_by_user_id(get_userid())
        return RESP_OK, {'lang': _lang}

    @api.doc(security=['tokenAuth'])
    @multi_auth.login_required
    @api.requestdecorator('GetUserLanguagePost', response_200={'lang': fields.String(example="hu", enum=["en", "hu"])})
    @update_last_auth_call
    @fmt_json_response_dict
    def post(self):
        """query current preferred user language"""
        _lang = users_user.get_preferred_language_by_user_id(get_userid())
        return RESP_OK, {'lang': _lang}


@api.route('bgservice/bgserviceexample')
class BgserviceExample(Resource):
    @bgservice_auth.login_required
    @update_last_auth_call
    @api.requestdecorator(
        'BgserviceExample',
        jsonfields={'value': fields.String(example="somestring", description="some input field", required=True)},
        response_200={'value': fields.String(example="somestring")},
        errors=[Errors.SETLANG_error_001])
    @fmt_json_response_dict
    @autocommit
    def post(self):
        """Example bgservice api endpoint"""
        return RESP_OK, {'value': api.payload["value"]}


###############################################################
########################    LEGACY    #########################
###############################################################

# ------------------------------------------------------------------
# ---- FUNCTIONAL API example with using the 'user' blueprint ------
# ------------------------------------------------------------------


# public w/o auth
@user.route('/public/getdata', methods=['GET', 'POST'])
@fmt_json_response
def get_data():

    return RESP_OK, {'public': "data", 'public2': "data2"}


# -----------------------------------------------------------------
# ---- FUNCTIONAL API example without json and req decorator ------
# -----------------------------------------------------------------


@user.route('/admin/listusers', methods=['GET'])
@multi_auth.login_required
def admin_rights_uid(user_id):
    return jsonify({'count': 1, 'result': [{'name': 'jozsi', 'user_id': 1}]})
    #db.session.commit()


# public w/o auth
@user.route('/public/getdataplainjson', methods=['GET', 'POST'])
def get_datajson():

    return jsonify({'public': "data", 'public2': "data2"})
