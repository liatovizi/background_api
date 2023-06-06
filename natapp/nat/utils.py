import logging
import secrets
from natapp import db
from natapp.users.db import user as users_user
from natapp.libs.naterrors import Errors
from natapp.nat.db import auth as natdb

logger = logging.getLogger(__name__)


class InstanceState:
    NOT_REGISTERED = 'not_registered'
    REGISTERED = 'registered'
    ACTIVATED = 'activated'


def generate_random_number(digits=8):
    s = "1234567890"
    return ''.join(secrets.choice(s) for x in range(digits))
