import hashlib
from datetime import datetime

from natapp.users import models as users_models
from natapp.users import utils as users_utils
from natapp.response import RESP_OK, RESP_ERR, RESP_OK_201
from natapp.libs.naterrors import Errors
import natapp.libs.natusers as userslib
import natapp.libs.natemailsender as natemailsender

bgservice_user_id = None


def init_bgservice_user(app, session):
    global bgservice_user_id

    try:
        user = app.config['BGSERVICE_API_USER']
        password = app.config['BGSERVICE_API_PASSWORD']
    except KeyError:
        raise ValueError('Bgservice API config is missing!')

    if len(user) == 0 or len(password) == 0:
        raise ValueError('Bgservice API config is invalid!')

    logins_rec = users_models.Logins.get_by_user_name(session, user)
    if logins_rec is None:
        # Create bgservice user
        user_rec = users_models.Users(
            email_address='',
            verification_level=-1,
            locked=0,
            privileges=userslib.AccessRights.PRIVILEGE_MASKS[userslib.AccessRights.BGSERVICE_USER])

        session.add(user_rec)
        session.flush()

        login_rec = users_models.Logins.create(user, users_utils.hash_password(password), user_rec.user_id)
        session.add(login_rec)

        session.commit()

        bgservice_user_id = user_rec.user_id

        app.logger.info(f'Created Dbfeeder user. ID={bgservice_user_id}')
    else:
        bgservice_user_id = logins_rec.user_id
        app.logger.info(f'Dbfeeder user ID={bgservice_user_id}')
