from natapp.users import models as users_models
from natapp.users import utils as users_utils
from natapp.nat import models as nat_models
from natapp.libs.naterrors import Errors
from natapp.response import RESP_OK, RESP_OK_201, RESP_ERR
import natapp.libs.natutility as nat_utils
import datetime
from natapp import db
from natapp.nat.db import nat as instancedb
from natapp.libs.natusers import AccessRights, get_user_access_rights
import re
from natapp.nat.utils import InstanceState, generate_random_number
import ujson
import logging
from datetime import datetime
from natapp.users.db import user as users_user

logger = logging.getLogger(__name__)


def handle_addepidemictrack(session, user_id, original_id, original_id_2, title, composer_id, composer_name,
                            metadata_tags, genres, moods, tempo_bpm, energy_level, release_date, url, duration, sha256):

    moods = [m.strip().lower() for m in moods.split(',')]
    metadata_tags = [m.strip().lower() for m in metadata_tags.split(',')]

    genres_parsed = []
    genres = [[gg.strip() for gg in g.split(',')] for g in genres.lower().split(':')]

    if len(genres) > 1:
        for i in range(1, len(genres) - 1):
            genres_parsed.append([genres[i - 1][-1], genres[i][:-1]])
        genres_parsed.append([genres[-2][-1], genres[-1]])

    # add track
    track = instancedb.add_track(
        user_id=user_id,
        original_id=original_id,
        original_id_2=original_id_2,
        catalog="epidemic",
        title=title,
        composer_id=composer_id,
        composer_name=composer_name,
        #metadata_tags=metadata_tags,
        #genres=genres,
        #moods=moods,
        tempo_bpm=tempo_bpm,
        energy_level=energy_level.lower(),
        release_date=release_date,
        url=url,
        duration=duration,
        sha256=sha256)

    # flush so we get the id
    db.session.flush()

    if not track or not track.track_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    # Collect tag ids
    tags = []
    for m in moods:
        mtags = instancedb.get_tags('mood', m)
        if len(mtags) == 1:
            tags.append(mtags[0])
        else:
            tags.append(instancedb.add_tag('mood', m))

    for m in metadata_tags:
        mtags = instancedb.get_tags('metadata', m)
        if len(mtags) == 1:
            tags.append(mtags[0])
        else:
            tags.append(instancedb.add_tag('metadata', m))

    for g in genres_parsed:
        for sg in g[1]:
            gtags = instancedb.get_tags('genre', g[0], sg)
            if len(gtags) == 1:
                tags.append(gtags[0])
            else:
                tags.append(instancedb.add_tag('genre', g[0], sg))

    # flush so we get all the ids
    db.session.flush()

    instancedb.add_tracktags(track.track_id, [t.tag_id for t in tags])

    return RESP_OK, {'track_id': str(track.track_id)}


def handle_listtracksbyepidemicid(session, user_id, tracks):
    # list tracks by epidemic ID
    track_ids = instancedb.list_track_ids_by_epidemic_id(tracks)
    return RESP_OK, [{'track_id': str(t[0]), 'original_id': t[1], 'original_id_2': t[2]} for t in track_ids]


def handle_updateplaylist(session, user_id, playlist_id, tracks):
    # find playlist with playlist_id
    pl = instancedb.get_playlist_by_id(playlist_id, with_for_update=True)

    if pl is None or not pl.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    plts = [t.playlist_id for t in instancedb.get_playlisttracks(playlist_id)]

    if plts != tracks:
        instancedb.add_playlisttracks(playlist_id, tracks)

    return RESP_OK, {}


def handle_removeplaylist(session, user_id, playlist_id):
    # find playlist with playlist_id
    pl = instancedb.get_playlist_by_id(playlist_id, with_for_update=True)

    if pl is None or not pl.playlist_id:
        return RESP_ERR, Errors.EGEN_invref_E002

    instancedb.remove_playlist(playlist_id)

    return RESP_OK, {}


def handle_getplaylists(session, user_id):

    playlists = instancedb.get_playlists_by_user_id(None, no_deleted=True)

    return RESP_OK, [{
        'playlist_id': str(p.playlist_id),
        'name': str(p.name),
        'external_url': p.external_url,
        'tracks': [str(t.track_id) for t in instancedb.get_playlisttracks(p.playlist_id)],
    } for p in playlists]


def handle_listplaylists(session, user_id, deleted=False):

    playlists = instancedb.get_playlists(deleted=deleted)

    return RESP_OK, [{
        'playlist_id': str(p.playlist_id),
        'deleted_at': p.deleted_at,
    } for p in playlists]
