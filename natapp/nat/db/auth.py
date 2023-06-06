from natapp import db

from natapp.users import models as users_models
from natapp.users.db import user as userdb
from natapp.nat import models as nat_models

from sqlalchemy import desc
from natapp.libs.natusers import AccessRights
import ujson
from datetime import datetime

import logging
from sqlalchemy import or_
from natapp.nat.utils import InstanceState

logger = logging.getLogger(__name__)


def get_instance_by_token(token):
    return db.session.query(nat_models.Instances).filter_by(token=token).first()


def update_instance_last_authorized_call(instance_id):
    i = db.session.query(nat_models.Instances).filter_by(instance_id=instance_id).with_for_update().first()
    i.last_authorized_call = round(datetime.now().timestamp() * 1000)
