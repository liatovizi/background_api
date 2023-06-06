from natapp import db

from natapp.users import models as users_models
from natapp.users.db import user as userdb
from natapp.nat import models as nat_models

from sqlalchemy import desc
from natapp.libs.natusers import AccessRights
import ujson
from datetime import datetime

import logging
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import aliased
from natapp.nat.utils import InstanceState
from natapp import db

from natapp.users import models as users_models
from natapp.users.db import user as userdb
from natapp.nat import models as nat_models

from sqlalchemy import desc
from natapp.libs.natusers import AccessRights
import ujson
from datetime import datetime

import logging
from sqlalchemy import or_, not_
from natapp.nat.utils import InstanceState

logger = logging.getLogger(__name__)


def add_instance(token):
    newinstance = nat_models.Instances(status=InstanceState.REGISTERED, token=token)
    db.session.add(newinstance)
    return newinstance


def get_instance_by_id(instance_id, with_for_update=False):
    if with_for_update:
        return db.session.query(nat_models.Instances).filter_by(instance_id=instance_id).with_for_update().first()
    return db.session.query(nat_models.Instances).filter_by(instance_id=instance_id).first()


def get_instance_by_activaiton_code(activation_code, with_for_update=False):
    if with_for_update:
        return db.session.query(
            nat_models.Instances).filter_by(activation_code=activation_code).with_for_update().first()
    return db.session.query(nat_models.Instances).filter_by(activation_code=activation_code).first()


def get_instances():
    return db.session.query(nat_models.Instances).all()


def get_instances_by_location_id(location_id, with_for_update=False):
    if with_for_update:
        return db.session.query(nat_models.Instances).filter_by(location_id=location_id).with_for_update().all()
    return db.session.query(nat_models.Instances).filter_by(location_id=location_id).all()


def add_location(user_id, name, country=None, state=None, city=None, zip=None, address=None):
    newloc = nat_models.Locations(user_id=user_id,
                                  name=name,
                                  country=country,
                                  state=state,
                                  city=city,
                                  zip=zip,
                                  address=address)
    db.session.add(newloc)
    return newloc


def get_location_by_id(location_id, with_for_update=False):
    if with_for_update:
        return db.session.query(nat_models.Locations).filter_by(location_id=location_id).with_for_update().first()
    return db.session.query(nat_models.Locations).filter_by(location_id=location_id).first()


def get_all_locations():
    return db.session.query(nat_models.Locations).filter_by().all()


def get_users_by_location_id(location_id, with_for_update=False):
    querystring = db.session.query(nat_models.LocationUsers).filter_by(location_id=location_id).join(
        users_models.Users, nat_models.LocationUsers.user_id == users_models.Users.user_id)
    if with_for_update:
        return querystring.with_for_update().all()
    return querystring.all()


def get_users_by_location_id(location_id, with_for_update=False):
    querystring = db.session.query(nat_models.LocationUsers).filter_by(location_id=location_id).join(
        users_models.Users, nat_models.LocationUsers.user_id == users_models.Users.user_id)
    if with_for_update:
        return querystring.with_for_update().all()
    return querystring.all()


def get_location_ids_by_user_ids(user_ids):
    if not isinstance(user_ids, list):
        user_ids = [user_ids]
    querystring = db.session.query(nat_models.LocationUsers.location_id).filter(
        nat_models.LocationUsers.user_id.in_(user_ids))
    return map(lambda x: x[0], querystring.all())


def get_all_users_with_privilege(privilege):
    return db.session.query(nat_models.LocationUsers, users_models.Users).join(
        users_models.Users, nat_models.LocationUsers.user_id == users_models.Users.user_id).filter(
            users_models.Users.privileges.op('&')(privilege) == privilege).all()


def get_all_users_with_privilege_for_location(privilege, location_id):
    return db.session.query(
        nat_models.LocationUsers, users_models.Users).filter(nat_models.LocationUsers.location_id == location_id).join(
            users_models.Users, nat_models.LocationUsers.user_id == users_models.Users.user_id).filter(
                users_models.Users.privileges.op('&')(privilege) == privilege).all()


def get_all_userslogins_with_privilege_for_location(privilege, location_id):
    return db.session.query(nat_models.LocationUsers, users_models.Users,
                            users_models.Logins).filter(nat_models.LocationUsers.location_id == location_id).join(
                                users_models.Users,
                                nat_models.LocationUsers.user_id == users_models.Users.user_id).join(
                                    users_models.Logins,
                                    users_models.Logins.user_id == users_models.Users.user_id).filter(
                                        users_models.Users.privileges.op('&')(privilege) == privilege).all()


def add_locationuser(user_id, location_id, pin_code=None, label=None):
    newlocusr = nat_models.LocationUsers(user_id=user_id, location_id=location_id, label=label, pin_code=pin_code)
    db.session.add(newlocusr)
    return newlocusr


def remove_locationuser(user_id, location_id):
    locusr = db.session.query(nat_models.LocationUsers).filter_by(user_id=user_id,
                                                                  location_id=location_id).with_for_update().all()
    if locusr == None:
        return False
    for l in locusr:
        db.session.delete(l)
    return True


def is_user_classcollective(user_id):
    if user_id == None:
        return False

    cnt = db.session.query(
        nat_models.LocationUsers, nat_models.Instances).filter(nat_models.LocationUsers.user_id == user_id).join(
            nat_models.Instances, nat_models.LocationUsers.location_id == nat_models.Instances.location_id).filter(
                nat_models.Instances.class_collective == True).count()
    return cnt > 0


def get_all_userslogins_with_privilege_for_location(privilege, location_id):
    return db.session.query(nat_models.LocationUsers, users_models.Users,
                            users_models.Logins).filter(nat_models.LocationUsers.location_id == location_id).join(
                                users_models.Users,
                                nat_models.LocationUsers.user_id == users_models.Users.user_id).join(
                                    users_models.Logins,
                                    users_models.Logins.user_id == users_models.Users.user_id).filter(
                                        users_models.Users.privileges.op('&')(privilege) == privilege).all()


def list_tracks(tracks=None):
    if tracks == None:
        tracks = db.session.query(nat_models.PlaylistTracks.track_id).distinct()
    tracks = db.session.query(nat_models.Tracks).filter(nat_models.Tracks.track_id.in_(tracks)).all()
    return tracks


def list_tracks_with_tags(tracks=None):
    if tracks == None:
        tracks = db.session.query(nat_models.PlaylistTracks.track_id).distinct()
    query = db.session.query(nat_models.Tracks, func.group_concat(nat_models.Tags.tag_id)).filter(
        nat_models.Tracks.track_id.in_(tracks))

    query = query.join(nat_models.TrackTags, nat_models.TrackTags.track_id == nat_models.Tracks.track_id)
    query = query.join(nat_models.Tags, nat_models.TrackTags.tag_id == nat_models.Tags.tag_id)
    query = query.filter(nat_models.Tags.type.in_(["genre", "mood"]))
    query = query.group_by(nat_models.Tracks)

    tracks = query.all()
    return tracks


def list_track_ids_by_epidemic_id(tracks):
    tracks_out = []
    for track in tracks:
        if track.get('original_id') is None and track.get('original_id_2') is None:
            raise ValueError('Error: track in API call with no original_id/original_id_2')
        t_filter = (nat_models.Tracks.catalog == "epidemic")
        if track.get('original_id') is not None:
            t_filter = t_filter & (nat_models.Tracks.original_id == track['original_id'])
        if track.get('original_id_2') is not None:
            t_filter = t_filter & (nat_models.Tracks.original_id_2 == track['original_id_2'])
        t = db.session.query(nat_models.Tracks.track_id, nat_models.Tracks.original_id,
                             nat_models.Tracks.original_id_2).filter(t_filter).all()
        if len(t) > 1:
            raise ValueError(
                f'Error: multiple tracks found by same original_id/original_id_2: {t["original_id"]}/{t["original_id_2"]}'
            )
        if len(t) == 1:
            tracks_out.append(t[0])
    return tracks_out


def list_tracks_with_filter_and_pagination(page,
                                           per_page,
                                           order_by=None,
                                           order=None,
                                           bpm_min=None,
                                           bpm_max=None,
                                           first_used_at_min=None,
                                           first_used_at_max=None,
                                           filters=None):
    # query all track ids that are used in a playlist (those are the available tracks on the microsite)
    track_ids = db.session.query(nat_models.PlaylistTracks.track_id).distinct()

    # start assembling the search filter by including tracks with the given ids
    # we return the Tracks object plus a group_concat field which will contain the genre and mood tags of the track
    query = db.session.query(nat_models.Tracks, func.group_concat(nat_models.Tags.tag_id)).filter(
        nat_models.Tracks.track_id.in_(track_ids))

    # apply bpm filters if present
    if bpm_min is not None:
        query = query.filter(nat_models.Tracks.tempo_bpm >= bpm_min)
    if bpm_max is not None:
        query = query.filter(nat_models.Tracks.tempo_bpm <= bpm_max)

    # apply first_used_at filters if present
    if first_used_at_min is not None:
        query = query.filter(nat_models.Tracks.first_used_at >= first_used_at_min)
    if first_used_at_max is not None:
        query = query.filter(nat_models.Tracks.first_used_at <= first_used_at_max)

    # apply othes simple filter if there is any; Items in the filter are "and"-ed together
    if filters is not None and filters != []:
        simplefilters = []
        tagfilters = []
        for f in filters:
            # a filter with empty values is skipped
            if f['values'] is None or f['values'] == []:
                continue

            filter = None
            tagfilter = None
            # handle the title filter
            if f['filter'] == 'title':
                # case insensitive like with the 1st element
                filter = nat_models.Tracks.title.ilike(f['values'][0])
                # if there are more than 1 values we append the other values with an "or" to the title filter
                for v in f['values'][1:]:
                    filter = filter | nat_models.Tracks.title.ilike(v)
                # finally append the filet ro our simple filters array (to be added to the query after the loops)
                simplefilters.append(filter)
            # composer filter, similar to title
            elif f['filter'] == 'composer_name':
                filter = nat_models.Tracks.composer_name.ilike(f['values'][0])
                for v in f['values'][1:]:
                    filter = filter | nat_models.Tracks.composer_name.ilike(v)
                simplefilters.append(filter)
            # energy_level filter, similar to title
            elif f['filter'] == 'energy_level':
                filter = nat_models.Tracks.energy_level == f['values'][0]
                for v in f['values'][1:]:
                    filter = filter | (nat_models.Tracks.energy_level == v)
                simplefilters.append(filter)
            # tegfilters come here, just specify the name and we will assemble later,, after the if to avoid having the same body in the if repeated multiple times
            elif f['filter'] == 'mood':
                tagfilter = 'mood'
            elif f['filter'] == 'genre':
                tagfilter = 'genre'
            elif f['filter'] == 'metadata':
                tagfilter = 'metadata'
            # if generic filter field is used we freate a compound query that searches in multiple fields
            elif f['filter'] == 'generic':
                if len(f['values']) != 1:
                    continue
                # we create an aliased name for tracktags and tags so we can push the filters and their respective tables to an array for later processing
                ttags = aliased(nat_models.TrackTags)
                atags = aliased(nat_models.Tags)
                # we assemble the filters - we search in title, composer_name, tag label and sublabel
                filter = nat_models.Tracks.title.ilike(f['values'][0]) | nat_models.Tracks.composer_name.ilike(
                    f['values'][0]) | atags.label.ilike(f['values'][0]) | atags.sublabel.ilike(f['values'][0])
                tagfilters.append([atags, ttags, filter])
                # query = query.join(ttags, ttags.track_id == nat_models.Tracks.track_id).join(atags, ttags.tag_id == atags.tag_id).filter(filter)

            # we assemble the tagfilter if we have 1 - similar to the generic
            if tagfilter is not None:
                # alias similar to the generic
                ttags = aliased(nat_models.TrackTags)
                atags = aliased(nat_models.Tags)
                # the genre filter is handled differently as there is a sublablel, too
                if tagfilter == 'genre':
                    tmp = f['values'][0].split(':')
                    if len(tmp) == 1:
                        filter = atags.label.ilike(tmp[0]) | atags.sublabel.ilike(tmp[0])
                    else:
                        filter = and_(atags.label.ilike(tmp[0]), atags.sublabel.ilike(tmp[1]))
                # other tag types only use the label field
                else:
                    filter = atags.label.ilike(f['values'][0])
                # we or the remaining parameters if there are any
                for v in f['values'][1:]:
                    if tagfilter == 'genre':
                        tmp = v.split(':')
                        if len(tmp) == 1:
                            filter = filter | atags.label.ilike(tmp[0]) | atags.sublabel.ilike(tmp[0])
                        else:
                            filter = filter | and_(atags.label.ilike(tmp[0]), atags.sublabel.ilike(tmp[1]))
                    else:
                        filter = filter | atags.label.ilike(v)
                # we add the assembled tag filter
                tagfilters.append([atags, ttags, filter])
                # query = query.join(ttags, ttags.track_id == nat_models.Tracks.track_id).join(atags, ttags.tag_id == atags.tag_id).filter(atags.type == tagfilter).filter(filter)

        # apply the simple filters
        for filt in simplefilters:
            query = query.filter(filt)
        # apply the tag filters
        for filt in tagfilters:
            query = query.join(filt[1], filt[1].track_id == nat_models.Tracks.track_id).join(
                filt[0], filt[1].tag_id == filt[0].tag_id).filter(filt[2])

    # we apply a distinct filter though dont sure it is necessary
    query = query.distinct()

    # we join the genre and mood labels
    query = query.join(nat_models.TrackTags, nat_models.TrackTags.track_id == nat_models.Tracks.track_id)
    query = query.join(nat_models.Tags, nat_models.TrackTags.tag_id == nat_models.Tags.tag_id)
    query = query.filter(nat_models.Tags.type.in_(["genre", "mood"]))

    # and do a group by so we will have the label id's in the group_concat field defined above in the query
    query = query.group_by(nat_models.Tracks)

    # apply orderings
    if order_by is not None:
        field = None
        if order_by == 'title':
            field = nat_models.Tracks.title
        elif order_by == 'composer_name':
            field = nat_models.Tracks.composer_name
        elif order_by == 'bpm':
            field = nat_models.Tracks.tempo_bpm
        elif order_by == 'energy_level':
            field = nat_models.Tracks.energy_level
        elif order_by == 'duration':
            field = nat_models.Tracks.duration
        elif order_by == 'first_used_at':
            field = nat_models.Tracks.first_used_at

        if field is not None:
            if order == 'descending':
                query = query.order_by(field.desc())
            else:
                query = query.order_by(field.asc())

    # apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return (pagination.total, pagination.items)


def get_playlist_by_id(playlist_id, with_for_update=False):
    if with_for_update:
        return db.session.query(nat_models.Playlists).filter_by(playlist_id=playlist_id).with_for_update().first()
    return db.session.query(nat_models.Playlists).filter_by(playlist_id=playlist_id).first()


def get_playlists_by_user_id(user_id, no_deleted=False):
    if no_deleted:
        return db.session.query(nat_models.Playlists).filter_by(user_id=user_id).filter_by(deleted_at=None).all()
    return db.session.query(nat_models.Playlists).filter_by(user_id=user_id).all()


def get_playlists(deleted=False):
    if deleted:
        return db.session.query(nat_models.Playlists).filter(nat_models.Playlists.deleted_at != None).all()
    return db.session.query(nat_models.Playlists).filter(nat_models.Playlists.deleted_at == None).all()


def get_system_and_user_playlists(user_id=None, class_collective=True):
    if user_id is None:
        query = db.session.query(nat_models.Playlists)
    else:
        query = db.session.query(nat_models.Playlists).filter((nat_models.Playlists.user_id == user_id)
                                                              | (nat_models.Playlists.system == True))
    if class_collective != True:
        query = query.filter(
            or_(nat_models.Playlists.class_collective == None, nat_models.Playlists.class_collective != True))
    return query.all()


def add_track(
        user_id,
        original_id,
        original_id_2,
        catalog,
        title,
        composer_id,
        composer_name,
        tempo_bpm,  # metadata_tags, genres, moods, tempo_bpm,
        energy_level,
        release_date,
        url,
        duration,
        sha256):
    newtrack = nat_models.Tracks(
        user_id=user_id,
        original_id=original_id,
        original_id_2=original_id_2,
        catalog=catalog,
        title=title,
        composer_id=composer_id,
        composer_name=composer_name,
        # metadata_tags=metadata_tags,
        # genres=genres,
        # moods=moods,
        tempo_bpm=tempo_bpm,
        energy_level=energy_level,
        release_date=release_date,
        url=url,
        duration=duration,
        sha256=sha256)
    db.session.add(newtrack)
    return newtrack


def add_playlist(user_id, name, meta, external_url=None, description=None, system=False):
    newpl = nat_models.Playlists(user_id=user_id,
                                 name=name,
                                 meta=meta,
                                 system=system,
                                 external_url=external_url,
                                 description=description)
    db.session.add(newpl)
    return newpl


def count_playlisttracks_by_track_id(track_id):
    # drop all playlisttracks
    count = db.session.query(nat_models.PlaylistTracks).filter_by(track_id=track_id).count()
    return count


def get_playlisttracks(playlist_id):
    # drop all playlisttracks
    pltracks = db.session.query(nat_models.PlaylistTracks).filter_by(playlist_id=playlist_id).order_by(
        nat_models.PlaylistTracks.rank.asc()).all()
    return pltracks


def remove_playlisttracks(playlist_id):
    # drop all playlisttracks
    pltracks = db.session.query(nat_models.PlaylistTracks).filter_by(playlist_id=playlist_id).all()
    for plt in pltracks:
        db.session.delete(plt)


def add_playlisttracks(playlist_id, tracks):
    # remove old ordering
    remove_playlisttracks(playlist_id)

    # add new ordering
    i = 1

    plts = []
    for track_id in tracks:
        newplt = nat_models.PlaylistTracks(rank=i, playlist_id=playlist_id, track_id=track_id)
        plts.append(newplt)
        db.session.add(newplt)
        i = i + 1

    db.session.query(nat_models.Tracks).filter(
        nat_models.Tracks.track_id.in_(tracks)).filter(nat_models.Tracks.first_used_at == None).update(
            values={'first_used_at': datetime.now()}, synchronize_session=False)

    return plts


def remove_playlist(playlist_id):
    pl = get_playlist_by_id(playlist_id, with_for_update=True)
    if pl is None:
        return False

    remove_playlisttracks(playlist_id)
    db.session.delete(pl)
    return True


def add_tag(type, label, sublabel=None):
    newtag = nat_models.Tags(type=type, label=label, sublabel=sublabel)
    db.session.add(newtag)
    return newtag


def get_tags(tag_type=None, label=None, sublabel=None, onlyused=False):
    query = db.session.query(nat_models.Tags)

    if type(tag_type) == type([]):
        query = query.filter(nat_models.Tags.type.in_(tag_type))
    elif tag_type is not None:
        query = query.filter_by(type=tag_type)
    if type(label) == type([]):
        query = query.filter(nat_models.Tags.label.in_(label))
    elif label is not None:
        query = query.filter_by(label=label)
    if type(sublabel) == type([]):
        query = query.filter(nat_models.Tags.sublabel.in_(sublabel))
    elif sublabel is not None:
        query = query.filter_by(sublabel=sublabel)

    if onlyused:
        tracks = db.session.query(nat_models.PlaylistTracks.track_id).distinct()
        tags = db.session.query(nat_models.TrackTags.tag_id).filter(
            nat_models.TrackTags.track_id.in_(tracks)).distinct()
        query = query.filter(nat_models.Tags.tag_id.in_(tags))

    return query.all()


def remove_tracktags(track_id):
    # drop all playlisttracks
    tracktags = db.session.query(nat_models.TrackTags).filter_by(track_id=track_id).all()
    for ttag in tracktags:
        db.session.delete(ttag)


def add_tracktags(track_id, tags):
    # remove old tags
    remove_tracktags(track_id)

    # add new ordering
    ttags = []
    for tag_id in tags:
        newttag = nat_models.TrackTags(track_id=track_id, tag_id=tag_id)
        ttags.append(newttag)
        db.session.add(newttag)

    return ttags


def update_telemetry(instance_id, sw_version, **params):
    # check if we already have a line for this instance
    count = db.session.query(nat_models.Telemetries).filter_by(instance_id=instance_id).count()

    if count == 0:
        telemetry = nat_models.Telemetries(instance_id=instance_id)
        db.session.add(telemetry)
    elif count == 1:
        telemetry = db.session.query(nat_models.Telemetries).filter_by(instance_id=instance_id).first()
    else:
        return False

    telemetry.sw_version = sw_version
    telemetry.device_timestamp = params.get('timestamp', None)
    telemetry.mem_free = params.get('mem_free', None)
    telemetry.mem_total = params.get('mem_total', None)
    telemetry.update_channel = params.get('update_channel', None)
    telemetry.eth0_ip = params.get('eth0_ip', None)
    telemetry.eth0_netmask = params.get('eth0_netmask', None)
    telemetry.eth0_gw = params.get('eth0_gw', None)
    telemetry.eth0_dns = params.get('eth0_dns', None)
    telemetry.eth0_mac = params.get('eth0_mac', None)

    return True


def get_instances_with_telemetry():
    return db.session.query(
        nat_models.Instances).join(nat_models.Telemetries,
                                   nat_models.Instances.instance_id == nat_models.Telemetries.instance_id,
                                   isouter=True).add_entity(nat_models.Telemetries).all()


def get_instances_with_telemetry_by_location_id(location_id):
    return db.session.query(nat_models.Instances).filter_by(location_id=location_id).join(
        nat_models.Telemetries, nat_models.Instances.instance_id == nat_models.Telemetries.instance_id,
        isouter=True).add_entity(nat_models.Telemetries).all()
