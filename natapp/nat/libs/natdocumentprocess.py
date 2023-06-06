from natapp.users import models as users_models
from natapp.nat import models as nat_models
from natapp.libs.naterrors import Errors
from natapp.response import RESP_OK, RESP_OK_201, RESP_ERR
from natapp.nat.db import auth as natdb
import natapp.libs.natutility as nat_utils
import datetime
from natapp import db
from natapp.nat.db import auth as natdb
from stellar_base.address import Address
from natapp.libs.natusers import AccessRights, get_user_access_rights
import re
from natapp.nat.utils import TaskState, TaskStatus, RequestStatus, NextTask, TaskLastAction, get_orgadmin_role
import ujson
import logging
from natapp.users.db import user as users_user

logger = logging.getLogger(__name__)

#def get_request_and_linked_new_task_by_request_id(session, request_id):
#    request = nat_models.Requests.get_by_id_with_lock(session, request_id)
#
#    if not request:
#        return None, None
#
#    task = nat_models.Tasks.clone_and_link(session, request.next_task_id)
#
#    if not task:
#        return None, None
#
#    return request, task
#
#
#
