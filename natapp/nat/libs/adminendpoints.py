from natapp.users import models as users_models
from natapp.users import utils as users_utils
from natapp.nat import models as nat_models
from natapp.libs.naterrors import Errors
from natapp.response import RESP_OK, RESP_OK_201, RESP_ERR
import natapp.libs.natutility as nat_utils
import datetime
from natapp import db
from natapp.nat.db import nat as natdb
from natapp.libs.natusers import AccessRights, get_user_access_rights, set_user_privilegesmask
import re
from natapp.nat.utils import InstanceState, generate_random_number
from natapp.users.db import user as userdb
import ujson
import logging
from datetime import datetime
from natapp.users.db import user as users_user

logger = logging.getLogger(__name__)


def handle_addlocation(session, user_id, name, country, state, city, zip, address):
    # create location object
    location = natdb.add_location(user_id=user_id,
                                  name=name,
                                  country=country,
                                  state=state,
                                  city=city,
                                  zip=zip,
                                  address=address)
    # flush so we get the id
    db.session.flush()

    if not location or not location.location_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    return RESP_OK, {'location_id': str(location.location_id)}


def handle_updatelocation(session, user_id, location_id, name, country, state, city, zip, address):
    # update location object

    location = natdb.get_location_by_id(location_id=location_id, with_for_update=True)

    if not location or not location.location_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    if name != None:
        location.name = name
    if country != None:
        location.country = country
    if state != None:
        location.state = state
    if city != None:
        location.city = city
    if zip != None:
        location.zip = zip
    if address != None:
        location.address = address

    return RESP_OK, {'location_id': str(location.location_id)}


def handle_listlocations(session, user_id):
    # find out if location exists
    locations = natdb.get_all_locations()

    locations = [{
        'location_id': str(loc.location_id),
        'name': loc.name,
        'country': loc.country,
        'state': loc.state,
        'city': loc.city,
        'zip': loc.zip,
        'address': loc.address,
        'instance_count': loc.instance_count,
    } for loc in locations]

    return RESP_OK, locations


def handle_activateinstance(session, user_id, activation_code, location_id, label=None):
    # find out if location exists
    location = natdb.get_location_by_id(location_id, with_for_update=True)

    if not location or not location.location_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    # find instance with the activation_code
    instance = natdb.get_instance_by_activaiton_code(activation_code, with_for_update=True)

    if not instance or not instance.instance_id:
        return RESP_ERR, Errors.EGEN_tokenref_E002

    if instance.status != InstanceState.REGISTERED:
        return RESP_ERR, Errors.ENAT_invstate_E001

    # update instance
    instance.status = InstanceState.ACTIVATED
    instance.activation_code = None
    instance.location_id = location_id
    instance.label = label

    location.instance_count = location.instance_count + 1

    return RESP_OK, {'location_id': str(location.location_id)}


def handle_deactivateinstance(session, user_id, instance_id):
    # find instance with the instance id
    instance = natdb.get_instance_by_id(instance_id, with_for_update=True)

    if not instance or not instance.instance_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    if instance.status != InstanceState.ACTIVATED:
        return RESP_ERR, Errors.ENAT_invstate_E001

    # find out if location exists
    location = natdb.get_location_by_id(instance.location_id, with_for_update=True)

    if not location or not location.location_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    # update instance
    instance.status = InstanceState.REGISTERED
    instance.location_id = None
    instance.label = None

    location.instance_count = location.instance_count - 1

    return RESP_OK, {'instance_id': str(instance.instance_id)}


def handle_updateinstance(session, user_id, instance_id, update_channel=None, class_collective=None):
    # update instance object
    instance = natdb.get_instance_by_id(instance_id=instance_id, with_for_update=True)

    if not instance or not instance.instance_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    if update_channel != None:
        instance.update_channel = update_channel
    if class_collective != None:
        instance.class_collective = class_collective
        instance.force_content_update = 5

    return RESP_OK, {'instance_id': str(instance.instance_id)}


def handle_listinstances_with_telemetry(session, user_id, location_id=None):
    if location_id is None:
        instances = natdb.get_instances_with_telemetry()
    else:
        instances = natdb.get_instances_with_telemetry_by_location_id(location_id)

    instances = [{
        'instance_id': str(i.instance_id),
        'location_id': (str(i.location_id) if i.location_id is not None else None),
        'label': i.label,
        'status': i.status,
        'update_channel': i.update_channel,
        'class_collective': i.class_collective,
        'last_authorized_call': i.last_authorized_call,
        'created_at': i.created_at,
        'telemetry': {
            'sw_version': t.sw_version,
            'update_channel': t.update_channel,
            'mem_free': t.mem_free,
            'mem_total': t.mem_total,
            'eth0_ip': t.eth0_ip,
            'eth0_netmask': t.eth0_netmask,
            'eth0_gw': t.eth0_gw,
            'eth0_dns': t.eth0_dns,
            'eth0_mac': t.eth0_mac,
        } if t is not None else None
    } for (i, t) in instances]

    return RESP_OK, instances


def handle_listinstances(session, user_id, location_id=None):
    if location_id is None:
        instances = natdb.get_instances()
    else:
        instances = natdb.get_instances_by_location_id(location_id)

    instances = [{
        'instance_id': str(i.instance_id),
        'location_id': (str(i.location_id) if i.location_id is not None else None),
        'label': i.label,
        'status': i.status,
        'update_channel': i.update_channel,
        'last_authorized_call': i.last_authorized_call,
        'created_at': i.created_at,
    } for i in instances]

    return RESP_OK, instances


def handle_listappusers(session, user_id):
    users = userdb.get_all_userslogins_with_privilege(AccessRights.PRIVILEGE_MASKS[AccessRights.TGGAPP_USER])

    users = [{
        'user_id': str(u.user_id),
        'email_address': u.email_address,
        'login_count': l.num_oflogs,
        'last_login': l.lastlog.timestamp() * 1000,
        'superuser': (u.privileges & AccessRights.PRIVILEGE_MASKS[AccessRights.TGGAPP_SUPERUSER]) > 0
    } for u, l in users]

    return RESP_OK, users


def handle_listapplocationusers(session, user_id, location_id=None):
    # list users activated for location
    if location_id is None:
        users = natdb.get_all_users_with_privilege(AccessRights.PRIVILEGE_MASKS[AccessRights.TGGAPP_USER])
    else:
        users = natdb.get_all_users_with_privilege_for_location(AccessRights.PRIVILEGE_MASKS[AccessRights.TGGAPP_USER],
                                                                location_id)

    users = [{
        'locationuser_id': str(ul.locationuser_id),
        'user_id': str(u.user_id),
        'location_id': str(ul.location_id),
        'email_address': u.email_address,
        'label': ul.label
    } for (ul, u) in users]

    return RESP_OK, users


def handle_addappuser(session, user_id, email_address, password):
    status, user = users_utils.regiser_new_user(username=email_address,
                                                password=password,
                                                email=email_address,
                                                newsletter=0,
                                                no_complexity_check=True)

    if status == "error":
        return RESP_ERR, user

    user.verification_level = 0
    user.locked = 0
    user.privileges = AccessRights.PRIVILEGE_MASKS[AccessRights.TGGAPP_USER]

    return RESP_OK, {'user_id': str(user.user_id)}


def handle_updateappuser(session, user_id, userrights, user_id_in, password=None, superuser=None):
    users = users_user.get_users_by_user_id(user_id_in)

    if users[0]['privileges'] & AccessRights.PRIVILEGE_MASKS[AccessRights.TGGAPP_USER] == 0:
        return RESP_ERR, Errors.EGEN_unauth_E001

    if password is not None:
        status, msg = users_utils.change_password(user_id=user_id_in, password=password, no_complexity_check=True)
        if status == "error":
            return RESP_ERR, msg
    if superuser is not None:
        set_user_privilegesmask(
            user_id_in, AccessRights.update_privilege(users[0]['privileges'], AccessRights.TGGAPP_SUPERUSER, superuser))

    return RESP_OK, {}


def handle_addapplocationuser(session, user_id, location_id, user_id_in, label, pin_code):
    locusr = natdb.add_locationuser(user_id=user_id_in, location_id=location_id, label=label, pin_code=pin_code)

    # flush so we get the id
    db.session.flush()

    if not locusr or not locusr.locationuser_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    return RESP_OK, {'locationuser_id': str(locusr.locationuser_id)}


def handle_removeapplocationuser(session, user_id, location_id, user_id_in):
    success = natdb.remove_locationuser(user_id=user_id_in, location_id=location_id)

    if not success:
        return RESP_ERR, Errors.EGEN_invref_E002

    return RESP_OK, {}


def handle_addplaylist(session, user_id, name, class_type, length_type, external_url):
    # create playlist object
    playlist = natdb.add_playlist(user_id=None,
                                  name=name,
                                  meta=f'{{"classType": "{class_type}", "lengthType": {length_type}}}',
                                  external_url=external_url,
                                  system=True)
    # flush so we get the id
    db.session.flush()

    if not playlist or not playlist.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    return RESP_OK, {'playlist_id': str(playlist.playlist_id)}


def handle_removeplaylist(session, user_id, playlist_id):
    # find playlist with playlist_id
    pl = natdb.get_playlist_by_id(playlist_id, with_for_update=True)

    if pl is None or not pl.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    natdb.remove_playlist(playlist_id)

    return RESP_OK, {}


def handle_listplaylists(session, user_id, user_id_in=None):

    if user_id_in is None:
        playlists = natdb.get_playlists(deleted=False)
    else:
        playlists = natdb.get_playlists_by_user_id(user_id_in, no_deleted=True)

    return RESP_OK, [{
        'playlist_id': str(p.playlist_id),
        'name': p.name,
        'meta': p.meta,
        'user_id': p.user_id,
        'description': p.description,
        'external_url': p.external_url
    } for p in playlists]


def handle_listtracks(session, user_id):
    tracks = natdb.list_tracks()
    tracks = [{
        'track_id': str(t.track_id),
        'title': t.title,
        'composer_name': t.composer_name,
        'first_used_at': t.first_used_at,
        'url': t.url,
    } for t in tracks]

    return RESP_OK, tracks
