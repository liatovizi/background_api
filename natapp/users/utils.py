import re
import hashlib, bcrypt
from flask import current_app as app
from natapp.libs.naterrors import Errors
from natapp.libs import natutility as nat_utils
from natapp.users.db import user as users_user
from natapp.users import utils as users_utils
from natapp import db
import natapp.libs.natusers as natusers
import secrets
import logging

logger = logging.getLogger(__name__)


def isint(s, logger):
    _isnum = re.compile(r"[-+]?[0-9]*\.?[0-9]*$")

    if type(s) is float or type(s) is int: return True
    if type(s) is not str:
        logger.debug(f"unknown type got: {type(s)}")
    return re.match(_isnum, s) is not None


def hash_password(password, rounds=None, hash_type="sha512-bcrypt"):
    if rounds == None:
        rounds = app.config['PASSWORD_HASH_DEFAULT_ROUNDS']
    if hash_type == "sha512-bcrypt":
        return f"sha512-bcrypt:{rounds}:" + hash_password_sha512_bcrypt(password, rounds)
    else:
        raise Exception(f"Unsupported hash type: {hash_type}")


def check_password(password, hash_value):
    if not hash_value:
        return False
    hash_array = hash_value.split(":")
    if hash_array[0] == "sha512-bcrypt":
        return check_password_sha512_bcrypt(password, hash_array[2])
    else:
        raise Exception(f"Unsupported hash type: {hash_array[0]}")


def hash_password_sha512_bcrypt(password, rounds=12):
    return bcrypt.hashpw(
        hashlib.sha512(password.encode('utf-8')).hexdigest().encode('utf-8'),
        bcrypt.gensalt(rounds=rounds)).decode('utf-8')


def check_password_sha512_bcrypt(password, hash_value):
    return bcrypt.checkpw(
        hashlib.sha512(password.encode('utf-8')).hexdigest().encode('utf-8'), hash_value.encode('utf-8'))


def regiser_new_user(username, password, email, newsletter, lang=None, no_complexity_check=False):
    _lang = "hu"
    if lang == "en":
        _lang = "en"
    else:
        logger.warning("Invalid preferred language!!")

    if len(username) < 5:
        return "error", Errors.EREG_badusr_E001
    if re.search('^[A-Z0-9a-z.!#@+]*$', username) is None:
        return "error", Errors.EREG_badusr_E002
    ### password validity check
    if not no_complexity_check and not nat_utils.check_password_format(password):
        return "error", Errors.EREG_badpwd_E001

    if not nat_utils.isValidEmail(email):
        return "error", Errors.EREG_invemail_E001
    c = users_user.get_users_by_email(email)
    if c:
        if c[0]['deleted']:
            return "error", Errors.EREG_badusr_E005
        return "error", Errors.EREG_badusr_E003

    c = users_user.get_logins_by_username(username)
    if c:
        usrs = users_user.get_users_by_user_id(c[0]['user_id'])
        if usrs[0]['deleted']:
            return "error", Errors.EREG_badusr_E006
        return "error", Errors.EREG_badusr_E004

    s = "abcdef1234567890-xyzk"
    verify_token = ''.join(secrets.choice(s) for x in range(29))

    newuser = users_user.add_user(email, 'dummy', -1, 1, verify_token, natusers.AccessRights.UNVERIFIED_EMAIL,
                                  newsletter, _lang)

    db.session.flush()

    if newuser.user_id:
        user_id = newuser.user_id
        users_user.add_login_data(username, users_utils.hash_password(password), user_id)

        return "ok", newuser

    # TODO What is 'incompleted' and why it is 201? Is it ok to create an inconsistent state in the DB?
    return "error", Errors.EGEN_dbresp_E001


def change_password(user_id, password, no_complexity_check=False):
    if not no_complexity_check and not nat_utils.check_password_format(password):
        return "error", Errors.EREG_badpwd_E001

    c = users_user.get_logins_by_userid(user_id)
    if c:
        usrs = users_user.get_users_by_user_id(c[0]['user_id'])
        if usrs[0]['deleted']:
            return "error", Errors.EREG_badusr_E006
        if usrs[0]['locked'] != 0:
            return "error", Errors.EGEN_lockedout_E001
        users_user.reset_password(user_id, users_utils.hash_password(password))
        return "ok", {}
    return "error", Errors.EREG_badusr_E004
