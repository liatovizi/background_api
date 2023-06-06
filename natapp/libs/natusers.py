import re
from natapp.users.db import user as users_user


class AccessRights:
    # TGGAPP_SUPERUSER : power user on the microsite who can access/edit othe user's playlists
    # TGGAPP_ADMIN : limited login to the admin ui
    # SUPER_ADMIN : full access to the admin ui

    UNVERIFIED_EMAIL, BGSERVICE_USER, NORMAL_USER, TGGAPP_ADMIN, TGGAPP_TABLET, SUPER_ADMIN, TGGAPP_USER, TGGAPP_SUPERUSER = range(
        8)

    PRIVILEGE_MASKS = {
        UNVERIFIED_EMAIL: 0b00000000,
        BGSERVICE_USER: 0b00000001,
        NORMAL_USER: 0b00000010,
        TGGAPP_ADMIN: 0b00000100,
        TGGAPP_TABLET: 0b00001000,
        TGGAPP_USER: 0b00010000,
        TGGAPP_SUPERUSER: 0b00100000,
        SUPER_ADMIN: 0b10000000,
    }

    @staticmethod
    def privileges_to_access_rights(privileges):
        return [access_right for access_right, mask in AccessRights.PRIVILEGE_MASKS.items() if privileges & mask]

    def update_privilege(privileges, access_right, value):
        if value == True:
            return privileges | AccessRights.PRIVILEGE_MASKS[access_right]

        currvalue = privileges & AccessRights.PRIVILEGE_MASKS[access_right]
        if currvalue == 0:
            return privileges
        else:
            return privileges ^ AccessRights.PRIVILEGE_MASKS[access_right]


def get_user_access_rights(user_id):
    rows = users_user.get_users_by_user_id(user_id)
    if rows is None:
        raise ValueError('DB error')

    if not rows:
        raise ValueError('Unknown user ID!')

    privileges = rows[0]['privileges']

    return AccessRights.privileges_to_access_rights(privileges)


def set_user_privilegesmask(user_id, privileges):
    users_user.set_user_privileges(user_id, privileges)


def get_user_privilegesmask(user_id):
    rows = users_user.get_users_by_user_id(user_id)
    if rows is None:
        raise ValueError('DB error')

    if not rows:
        raise ValueError('Unknown user ID!')

    return rows[0]['privileges']
