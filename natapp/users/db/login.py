import hashlib
from natapp import db
from natapp.users import models as users_models
from natapp.users import utils as users_utils

ACCESS_TOKEN_VALIDITY = 10000
REFRESH_TOKEN_VALIDITY = 64000
REFRESH_MAX_USER_INACTIVITY = 9900


def get_user(username):
    l = db.session.query(users_models.Logins.password,
                         users_models.Logins.user_id).filter_by(user_name=username).first()
    if l is None:
        return None
    return dict(password=l[0], user_id=l[1])


def check_password(user_id, password):
    l = db.session.query(users_models.Logins.password, users_models.Logins.user_id)\
        .filter_by(user_id=user_id).first()
    if l is None:
        return False
    return users_utils.check_password(password, l.password)


def get_user_by_email(email):
    user = db.session.query(users_models.Users).filter_by(email_address=email).first()
    if user is None:
        return None

    # Read the value from the resultset
    user_id = user.user_id

    login_rec = db.session.query(users_models.Logins.password)\
                          .filter_by(user_id=user_id).first()
    if login_rec is None:
        return None

    return dict(password=login_rec.password, user_id=user_id, privileges=user.privileges)


def add_token(user_id, token, renew, valid_to, renewable_to):
    #db.exec("INSERT INTO tokens (user_id, token, renew, valid_to, renewable_to) VALUES (" +
    #        user_id + ",'" + token + "','" + renew + "','" + str(exp) + "','" + str(exp) + "'," +
    #        ")", commit=True)
    db.session.add(
        users_models.Tokens(user_id=user_id, token=token, renew=renew, valid_to=valid_to, renewable_to=renewable_to))


def drop_token(_token):
    tokens = db.session.query(users_models.Tokens).filter_by(token=_token).all()
    if tokens:
        db.session.delete(tokens[0])


def drop_tokens_by_user_id(_user_id):
    tokens = db.session.query(users_models.Tokens).filter_by(user_id=_user_id).all()
    if tokens:
        for t in tokens:
            db.session.delete(t)


def get_tokens(_token):
    # db.fetchall("SELECT * from tokens where token='" + str(_token) + "'")
    return db.session.query(users_models.Tokens).filter_by(token=_token).first()


def get_renew_tokens(_token):
    # db.fetchall("SELECT * from tokens where token='" + str(_token) + "'")
    return [t.__dict__ for t in db.session.query(users_models.Tokens).filter_by(renew=_token).all()]


def renew_token(new_access_token, new_refresh_token, new_exp, new_renew, old_refresh_token):
    # db.exec("UPDATE tokens set token='" + _token + "', valid_to='" + str(_exp) + "' where token='" + request.json[
    #                'access_token'] + "' and renew='" + request.json['refresh_token'] + "'", commit=True)
    db.session.query(users_models.Tokens).filter_by(renew=old_refresh_token).update({
        users_models.Tokens.token:
        new_access_token,
        users_models.Tokens.renew:
        new_refresh_token,
        users_models.Tokens.valid_to:
        new_exp,
        users_models.Tokens.renewable_to:
        new_renew
    })


def update_data(_user_id, _remote_addr):
    l = db.session.query(users_models.Logins).filter_by(user_id=_user_id).with_for_update().first()
    l.num_oflogs = l.num_oflogs + 1
    l.lastlog = db.func.now()
    l.last_login_ip = _remote_addr


def update_user_last_authorized_call(user_id):
    u = db.session.query(users_models.Users).filter_by(user_id=user_id).first()
    u.last_authorized_call = db.func.now()


def get_user_last_authorized_call(user_id):
    u = db.session.query(users_models.Users).filter_by(user_id=user_id).first()
    return u.last_authorized_call if u is not None else None
