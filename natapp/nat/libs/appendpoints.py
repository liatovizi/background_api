from natapp.users import models as users_models
from natapp.users import utils as users_utils
from natapp.nat import models as nat_models
from natapp.libs.naterrors import Errors
from natapp.response import RESP_OK, RESP_OK_201, RESP_ERR
from natapp.nat.db import auth as natdb
import natapp.libs.natutility as nat_utils
import datetime
from natapp import db
from natapp.nat.db import nat as instancedb
from natapp.libs.natusers import AccessRights, get_user_access_rights
import re
from natapp.nat.utils import InstanceState, generate_random_number
import ujson
import logging
import fcntl
from datetime import datetime
from natapp.users.db import user as users_user
from flask import current_app as app

logger = logging.getLogger(__name__)


def handle_registerinstance(session):
    # generate token for device
    token = nat_utils.gen_password(128)
    # ceeate instance object
    instance = instancedb.add_instance(token)
    #flush so we get the id
    db.session.flush()

    if not instance or not instance.instance_id:
        return RESP_ERR, Errors.EGEN_dbresp_E001

    return RESP_OK, {'instance_id': str(instance.instance_id), 'access_token': token}


def handle_getactivationcode(session, instance_id):
    instance = instancedb.get_instance_by_id(instance_id, with_for_update=True)

    if not instance or not instance.instance_id:
        return RESP_ERR, Errors.EGEN_dbresp_E001

    if instance.status != InstanceState.REGISTERED:
        return RESP_ERR, Errors.ENAT_invstate_E001

    activation_code = generate_random_number()
    instance.activation_code = activation_code

    return RESP_OK, {'activation_code': activation_code}


def handle_heartbeat(session,
                     instance_id,
                     status,
                     version=None,
                     instance_id_in=None,
                     timestamp=None,
                     sw_version=None,
                     logs=None,
                     logdir=None,
                     telemetry=None):
    if instance_id_in is not None and instance_id != instance_id_in:
        return RESP_ERR, Errors.EGEN_unauth_E002

    instance = instancedb.get_instance_by_id(instance_id, with_for_update=True)

    # write telemetry if any
    if version is not None and version >= 1:
        telemetries = {'timestamp': timestamp, 'sw_version': sw_version}
        # we handle log version 1 +
        if telemetry is not None:
            parsed = ujson.loads(telemetry)
            if 'memFree' in parsed:
                telemetries['mem_free'] = parsed['memFree']
            if 'memTotal' in parsed:
                telemetries['mem_total'] = parsed['memTotal']
            if 'network' in parsed and 'interfaces' in parsed['network'] and 'eth0' in parsed['network'][
                    'interfaces'] and len(parsed['network']['interfaces']['eth0']) == 1:
                tempvar = parsed['network']['interfaces']['eth0'][0]
                if 'address' in tempvar:
                    telemetries['eth0_ip'] = tempvar['address']
                if 'netmask' in tempvar:
                    telemetries['eth0_netmask'] = tempvar['netmask']
                if 'mac' in tempvar:
                    telemetries['eth0_mac'] = tempvar['mac']
        if logs is not None and logs != '' and logdir is not None and logdir != '':
            logs = re.sub("\[object Object\]", "", logs)
            parsedlogs = ""
            if instance.location_id is not None:
                logarr = []
                for line in logs.split('\n'):
                    if line != '':
                        try:
                            obj = ujson.loads(line.strip(' \t\r\n\0'))
                        except ValueError as e:
                            logger.error(f"Invalid JSON in heartbeat from instance {instance_id}: {line}")
                            continue
                        if 'instance' in obj and obj['instance'] != str(instance_id_in):
                            logger.warning(
                                f"Logline with instance id not belonging to the authenticated instance! auth id: {instance_id}; in the logs: {obj['instance']} "
                            )
                            continue
                        if 'instance' not in obj:
                            obj['instance'] = str(instance_id)
                        obj['location_id'] = str(instance.location_id)
                        logarr.append(ujson.dumps(obj))
                    else:
                        logarr.append('')
                parsedlogs = '\n'.join(logarr)
            with open(logdir + '/' + str(instance_id) + '.log', "a") as myfile:
                fcntl.flock(myfile, fcntl.LOCK_EX)
                myfile.write(re.sub("\[object Object\]", "", parsedlogs))
                fcntl.flock(myfile, fcntl.LOCK_UN)
        instancedb.update_telemetry(instance_id=instance_id, **telemetries)

    resp = {'status': instance.status}
    if instance.update_channel is not None and instance.update_channel in ['alpha', 'beta', 'stable']:
        resp['update_channel'] = instance.update_channel

    if instance.force_sw_update is not None and instance.force_sw_update > 0:
        instance.force_sw_update -= 1
        resp['sw_update'] = True

    if instance.force_content_update is not None and instance.force_content_update > 0:
        instance.force_content_update -= 1
        resp['content_update'] = True

    return RESP_OK, resp


def handle_checkuserpin(session, instance_id, status, pin_code):
    instance = instancedb.get_instance_by_id(instance_id)

    if status != InstanceState.ACTIVATED:
        return RESP_ERR, Errors.ENAT_notactivated_E001

    locusers = instancedb.get_all_userslogins_with_privilege_for_location(0, instance.location_id)
    for (lu, u, l) in locusers:
        if lu.pin_code == pin_code:
            return RESP_OK, {'success': True, 'user_id': str(lu.user_id)}

    return RESP_OK, {
        'success': False,
    }


def handle_getlayout(session, instance_id, status, user_id=None):

    if status != InstanceState.ACTIVATED:
        return RESP_ERR, Errors.ENAT_notactivated_E001

    instance = instancedb.get_instance_by_id(instance_id)

    json_file = app.config['LAYOUT_JSON_FILE']
    if instance.class_collective == True:
        json_file = app.config['LAYOUT_JSON_FILE_CC']

    with open(json_file) as f:
        respdata = ujson.load(f)

    return RESP_OK, respdata


def handle_listplaylists(session, instance_id, status, user_id=None):

    if status != InstanceState.ACTIVATED:
        return RESP_ERR, Errors.ENAT_notactivated_E001

    playlists = instancedb.get_playlists_by_user_id(user_id, no_deleted=True)

    return RESP_OK, [{
        'playlist_id': str(p.playlist_id),
        'name': p.name,
        'tracks': [str(t.track_id) for t in instancedb.get_playlisttracks(p.playlist_id)],
        'meta': p.meta,
        'description': p.description,
        'class_collective': True if p.class_collective == True else False
    } for p in playlists if p.hidden is not True]


def handle_gettrackfiles(session, instance_id, status, tracks=None):

    if status != InstanceState.ACTIVATED:
        return RESP_ERR, Errors.ENAT_notactivated_E001

    # TODO maybe validate that only available tracks are asked for..?
    if tracks is None:
        tracks = instancedb.list_tracks()
    else:
        tracks = instancedb.list_tracks([int(id) for id in tracks])
    tracks = [{
        'track_id': str(t.track_id),
        'duration': t.duration,
        'title': t.title,
        'artist': t.composer_name,
        'sha256': t.sha256,
        'url': t.url,
    } for t in tracks]

    return RESP_OK, tracks
