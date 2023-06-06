from natapp import db
from natapp.users import models as users_models


def get_users_by_email(_email):
    #c = db.fetchall("SELECT user_id from users where email_address='" + email + "'")
    return [u.__dict__ for u in db.session.query(users_models.Users).filter_by(email_address=_email).all()]


def get_users_by_user_id(user_id):
    return [u.__dict__ for u in db.session.query(users_models.Users).filter_by(user_id=user_id).all()]


def get_all_users():
    return [u.__dict__ for u in db.session.query(users_models.Users).all()]


def get_all_users_with_privilege(privilege):
    return [
        u.__dict__ for u in db.session.query(users_models.Users).filter(
            users_models.Users.privileges.op('&')(privilege) > 0).all()
    ]


def get_all_userslogins_with_privilege(privilege):
    return db.session.query(users_models.Users,
                            users_models.Logins).filter(users_models.Users.privileges.op('&')(privilege) > 0).join(
                                users_models.Logins, users_models.Users.user_id == users_models.Logins.user_id).all()


def get_locked_users_by_validity_token(_vtoken):
    #c = db.fetchall("SELECT user_id from users where validity_token='" + request.args['token'] + "'")
    return [u.__dict__ for u in db.session.query(users_models.Users).filter_by(validity_token=_vtoken, locked=1).all()]


def get_logins_by_username(_name):
    #c = db.fetchall("SELECT login_id from logins where user_name='" + usr + "'")
    return [u.__dict__ for u in db.session.query(users_models.Logins).filter_by(user_name=_name).all()]


def get_logins_by_userid(_id):
    #c = db.fetchall("SELECT login_id from logins where user_name='" + usr + "'")
    return [u.__dict__ for u in db.session.query(users_models.Logins).filter_by(user_id=_id).all()]


def add_user(_email, _kyc_token, _verification_level, _locked, _verify_token, _default_privileges, _newsletter,
             _language):
    #db.exec("INSERT INTO users (email_address,kyc_token,verification_level) VALUES ('" + email + "','dummmy',-1)", commit=True)
    newuser = users_models.Users(email_address=_email,
                                 kyc_token=_kyc_token,
                                 verification_level=_verification_level,
                                 locked=_locked,
                                 validity_token=_verify_token,
                                 privileges=_default_privileges,
                                 newsletter=_newsletter,
                                 language=_language)
    db.session.add(newuser)
    return newuser


def add_login_data(_user_name, _password, _user_id):
    #db.exec("INSERT INTO users (email_address,kyc_token,verification_level) VALUES ('" + email + "','dummmy',-1)", commit=True)
    db.session.add(users_models.Logins(user_name=_user_name, password=_password, user_id=_user_id))


def add_balance(_user_id, _coin_id, _balance, _pending, _locked):
    # db.exec("INSERT INTO balances (user_id, coin_id, balance,pending,locked) VALUES ('" + user_id + "','0','0.0',0,0)")
    db.session.add(
        exchange_models.Balances(user_id=_user_id, coin_id=_coin_id, balance=_balance, pending=_pending,
                                 locked=_locked))


def set_email_verify_sent(user_id):
    # db.exec("UPDATE users set verification_level=0 where user_id=" + str(uid), commit=True)
    x = db.session.query(users_models.Users).filter_by(user_id=user_id).first()
    x.email_verify_sent = db.func.now()


def validate_user(_user_id, _vtoken, _verified_privileges):
    #db.exec("UPDATE users set locked=0 where validity_token='" + request.args['token'] + "' and user_id=" + user_id, commit=True)
    db.session.query(users_models.Users).filter_by(validity_token=_vtoken, user_id=_user_id).update({
        'locked':
        0,
        'privileges':
        _verified_privileges
    })


def set_reset_pwd_token(user_id, _reset_pwd_token):
    x = db.session.query(users_models.Users).filter_by(user_id=user_id).first()
    x.resetpwd_token = _reset_pwd_token
    x.email_resetpwd_sent = db.func.now()


def get_users_by_reset_pwd_token(_reset_pwd_token):
    return [u.__dict__ for u in db.session.query(users_models.Users).filter_by(resetpwd_token=_reset_pwd_token).all()]


def reset_password(user_id, _passwd):
    l = db.session.query(users_models.Logins).filter_by(user_id=user_id).first()
    l.password = _passwd
    u = db.session.query(users_models.Users).filter_by(user_id=user_id).first()
    u.resetpwd_token = None
    u.email_resetpwd_sent = None


def set_user_privileges(user_id, privileges):
    x = db.session.query(users_models.Users).filter_by(user_id=user_id).first()
    x.privileges = privileges


def set_user_preferred_language(_user_id, _language):
    x = db.session.query(users_models.Users).filter_by(user_id=_user_id).first()
    x.language = _language


def get_preferred_language_by_user_id(_user_id):
    lang = db.session.query(users_models.Users.language).filter_by(user_id=_user_id).first()
    return lang
