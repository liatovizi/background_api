from natapp.users import models as users_models
from natapp.users import utils as users_utils
from natapp.nat import models as nat_models
from natapp.libs.naterrors import Errors
from natapp.response import RESP_OK, RESP_OK_201, RESP_ERR
import natapp.libs.natutility as nat_utils
import datetime
from natapp import db
from natapp.nat.db import nat as natdb
from natapp.libs.natusers import AccessRights, get_user_access_rights
import re
from natapp.nat.utils import InstanceState, generate_random_number
from natapp.users.db import user as userdb
import ujson
import logging
from datetime import datetime
from natapp.users.db import user as users_user
from flask import current_app as app

logger = logging.getLogger(__name__)


def handle_listappusers(session, user_id):
    users = userdb.get_all_userslogins_with_privilege(AccessRights.PRIVILEGE_MASKS[AccessRights.TGGAPP_USER])

    users = [
        {
            'user_id': str(u.user_id),
            'email_address': u.email_address,
            #  'superuser': (u.privileges & AccessRights.PRIVILEGE_MASKS[AccessRights.TGGAPP_SUPERUSER]) > 0
        } for u, l in users
    ]

    return RESP_OK, users


def handle_addplaylist(session, user_id, userrights, user_id_in, name, description, tracks):
    # only superuser can add in the name of othe users
    if user_id != user_id_in:
        if AccessRights.TGGAPP_SUPERUSER not in userrights:
            return RESP_ERR, Errors.EGEN_unauth_E001
        elif len(users_user.get_users_by_user_id(user_id_in)) == 0:
            return RESP_ERR, Errors.EGEN_invref_E002

    # create playlist object
    playlist = natdb.add_playlist(user_id=user_id_in,
                                  description=description,
                                  name=name,
                                  meta=f'{{"classType": "custom"}}',
                                  system=False)
    # flush so we get the id
    db.session.flush()
    if not playlist or not playlist.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    if tracks != [] and tracks is not None:
        for t in tracks:
            if natdb.count_playlisttracks_by_track_id(t) == 0:
                return RESP_ERR, Errors.EGEN_invref_E002

        natdb.add_playlisttracks(playlist.playlist_id, tracks)
        for lid in natdb.get_location_ids_by_user_ids(user_id_in):
            instances = natdb.get_instances_by_location_id(lid, with_for_update=True)
            for instance in instances:
                instance.force_content_update = 2

    return RESP_OK, {'playlist_id': str(playlist.playlist_id)}


def handle_updateplaylist(session, user_id, userrights, playlist_id, name=None, description=None, tracks=None):
    # create playlist object
    p = natdb.get_playlist_by_id(playlist_id, with_for_update=True)

    if p is None or not p.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    if p is None or not p.playlist_id or p.system or (userrights is not None
                                                      and AccessRights.TGGAPP_SUPERUSER not in userrights and
                                                      (p.user_id is not None and p.user_id != user_id)):
        return RESP_ERR, Errors.EGEN_unauth_E001

    changed = False

    if name is not None:
        if p.name != name:
            changed = True
        p.name = name

    if description is not None:
        if p.description != description:
            changed = True
        p.description = description

    if tracks is not None:
        plts = [t.playlist_id for t in natdb.get_playlisttracks(playlist_id)]
        if plts != tracks:
            for t in tracks:
                if natdb.count_playlisttracks_by_track_id(t) == 0:
                    return RESP_ERR, Errors.EGEN_invref_E002

            natdb.add_playlisttracks(playlist_id, tracks)
            changed = True

    if changed:
        for lid in natdb.get_location_ids_by_user_ids(p.user_id):
            instances = natdb.get_instances_by_location_id(lid, with_for_update=True)
            for instance in instances:
                instance.force_content_update = 2

    return RESP_OK, {}


def handle_removeplaylist(session, user_id, userrights, playlist_id):
    # find playlist with playlist_id
    p = natdb.get_playlist_by_id(playlist_id, with_for_update=True)

    if p is None or not p.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    if p is None or not p.playlist_id or p.system or (userrights is not None
                                                      and AccessRights.TGGAPP_SUPERUSER not in userrights and
                                                      (p.user_id is not None and p.user_id != user_id)):
        return RESP_ERR, Errors.EGEN_unauth_E001

    if p.deleted_at is not None:
        return RESP_ERR, Errors.ENAT_pldeleted_E001

    p.deleted_at = datetime.now()

    if p.user_id is not None:
        for lid in natdb.get_location_ids_by_user_ids(p.user_id):
            instances = natdb.get_instances_by_location_id(lid, with_for_update=True)
            for instance in instances:
                instance.force_content_update = 2

    return RESP_OK, {}


def handle_restoreplaylist(session, user_id, userrights, playlist_id):
    # find playlist with playlist_id
    p = natdb.get_playlist_by_id(playlist_id, with_for_update=True)

    if p is None or not p.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    if p is None or not p.playlist_id or p.system or (userrights is not None
                                                      and AccessRights.TGGAPP_SUPERUSER not in userrights and
                                                      (p.user_id is not None and p.user_id != user_id)):
        return RESP_ERR, Errors.EGEN_unauth_E001

    if p.deleted_at is None:
        return RESP_ERR, Errors.ENAT_plnotdeleted_E001

    p.deleted_at = None

    if p.user_id is not None:
        for lid in natdb.get_location_ids_by_user_ids(p.user_id):
            instances = natdb.get_instances_by_location_id(lid, with_for_update=True)
            for instance in instances:
                instance.force_content_update = 2

    return RESP_OK, {}


def handle_getlayout(session, user_id=None, userrights=None):
    json_file = app.config['LAYOUT_JSON_FILE']
    if natdb.is_user_classcollective(user_id) or (userrights is not None
                                                  and AccessRights.TGGAPP_SUPERUSER in userrights):
        json_file = app.config['LAYOUT_JSON_FILE_CC']

    with open(json_file) as f:
        respdata = ujson.load(f)

    return RESP_OK, respdata


def handle_listplaylists(session, user_id, userrights):
    is_cc = natdb.is_user_classcollective(user_id)

    if userrights is not None and AccessRights.TGGAPP_SUPERUSER in userrights:
        playlists = natdb.get_system_and_user_playlists(class_collective=is_cc)
    else:
        playlists = natdb.get_system_and_user_playlists(user_id=user_id, class_collective=is_cc)

    return RESP_OK, [{
        'playlist_id': str(p.playlist_id),
        'name': p.name,
        'user_id': str(p.user_id),
        'meta': p.meta,
        'description': p.description,
        'class_collective': True if p.class_collective == True else False,
        'deleted': p.deleted_at is not None
    } for p in playlists if p.hidden is not True and (is_cc or p.class_collective is not True)]


def handle_getplaylist(session, user_id, userrights, playlist_id):
    p = natdb.get_playlist_by_id(playlist_id)

    if p is None or not p.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    if p is None or not p.playlist_id or (userrights is not None and AccessRights.TGGAPP_SUPERUSER not in userrights and
                                          (p.user_id is not None and p.user_id != user_id)) or p.hidden is True:
        return RESP_ERR, Errors.EGEN_unauth_E001

    return RESP_OK, {
        'playlist_id': str(p.playlist_id),
        'name': p.name,
        'tracks': [str(t.track_id) for t in natdb.get_playlisttracks(p.playlist_id)],
        'meta': p.meta,
        'description': p.description,
        'deleted': p.deleted_at is not None
    }


def handle_listtags(session, user_id):
    tags = [{'type': t.type, 'label': t.label, 'sublabel': t.sublabel} for t in natdb.get_tags()]
    return RESP_OK, tags


def handle_listfiltertags(session, user_id):
    tags = [{
        'type': t.type,
        'label': t.label,
        'sublabel': t.sublabel
    } for t in natdb.get_tags(tag_type=["genre", "mood", "energy_level"], onlyused=True)]
    return RESP_OK, tags


def handle_searchlibrary(session,
                         user_id,
                         page,
                         per_page,
                         order=None,
                         order_by=None,
                         bpm_min=None,
                         bpm_max=None,
                         first_used_at_min=None,
                         first_used_at_max=None,
                         filters=None):
    count, tracks = natdb.list_tracks_with_filter_and_pagination(page=page,
                                                                 per_page=per_page,
                                                                 order=order,
                                                                 order_by=order_by,
                                                                 bpm_min=bpm_min,
                                                                 bpm_max=bpm_max,
                                                                 first_used_at_min=first_used_at_min,
                                                                 first_used_at_max=first_used_at_max,
                                                                 filters=filters)

    data = [{
        'track_id': str(t.track_id),
        'title': t.title,
        'composer_name': t.composer_name,
        'duration': t.duration,
        'tag_ids': tags.split(",") if tags is not None else [],
        'bpm': t.tempo_bpm,
        'url': t.url,
        'energy_level': t.energy_level,
        'first_used_at': t.first_used_at,
    } for t, tags in tracks]

    return RESP_OK, {'page': page, 'per_page': per_page, 'items': count, 'data': data}


#        return RESP_OK, {
#            'page': page,
#            'per_page': per_page,
#            'items': 6,
#            'data': [
#                {'track_id': "1", 'title': "Halleluja", 'artist': 'Cucu cica', 'duration': 157, 'genre': 'pop', 'energy_level': 'mid', 'bpm': 155, 'url': nat.config['API_ENDPOINT'] + '/../../../static/1.mp3'},
#                {'track_id': "2", 'title': "Kokós Jumbo", 'artist': 'Kozsó', 'duration': 143, 'genre': 'rock', 'energy_level': 'high', 'bpm': 195, 'url': nat.config['API_ENDPOINT'] + '/../../../static/2.mp3'},
#                {'track_id': "3", 'title': "Isten", 'artist': 'fia', 'duration': 194, 'genre': 'opera', 'energy_level': 'low', 'bpm': 15, 'url': nat.config['API_ENDPOINT'] + '/../../../static/3.mp3'},
#                {'track_id': "4", 'title': "Halleluja (ogg)", 'artist': 'Cucu cica', 'duration': 157, 'genre': 'pop', 'energy_level': 'mid', 'bpm': 155, 'url': nat.config['API_ENDPOINT'] + '/../../../static/1.ogg'},
#                {'track_id': "5", 'title': "Kokós Jumbo (ogg)", 'artist': 'Kozsó',  'duration': 143, 'genre': 'rock', 'energy_level': 'high', 'bpm': 195, 'url': nat.config['API_ENDPOINT'] + '/../../../static/2.ogg'},
#                {'track_id': "6", 'title': "Isten (ogg)", 'artist': 'fia', 'duration': 194, 'genre': 'opera', 'energy_level': 'low', 'bpm': 15, 'url': nat.config['API_ENDPOINT'] + '/../../../static/3.ogg'},
#            ],
#        }


def handle_gettrackfiles(session, user_id, tracks):
    if tracks == []:
        return RESP_OK, []

    # filter duplicates from tracks
    tracks = list(set(tracks))
    tracks2 = natdb.list_tracks_with_tags([int(id) for id in tracks])

    # return with error if there are missing track ids
    if len(tracks2) != len(tracks):
        return RESP_ERR, Errors.EGEN_invref_E002

    # return with error if there are tracks that can't be used
    for t in tracks2:
        if natdb.count_playlisttracks_by_track_id(t[0].track_id) == 0:
            return RESP_ERR, Errors.EGEN_invref_E002

    tracks3 = [{
        'track_id': str(t.track_id),
        'duration': t.duration,
        'title': t.title,
        'composer_name': t.composer_name,
        'tag_ids': tags.split(",") if tags is not None else [],
        'bpm': t.tempo_bpm,
        'energy_level': t.energy_level,
        'url': t.url,
        'first_used_at': t.first_used_at,
    } for t, tags in tracks2]

    return RESP_OK, tracks3
