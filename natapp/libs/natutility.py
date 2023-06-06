import socket
import re
import fcntl
import secrets


def get_lock(process_name):
    """
    Acquires a lock using a UNIX domain socket. Works on Linux only.
    :param process_name:
    :return:
    """
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        get_lock._lock_socket.bind('\0' + process_name)
    except socket.error as e:
        # TODO logging ?
        return False
    return True


def get_lock_file(pid_file='bgservice.lock'):
    """
    Acquires a lock using a lock file. Works on Unixes.
    :param pid_file:
    :return:
    """
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    return True


def set_bit(v, index, x):
    mask = 1 << index
    v &= ~mask
    if x:
        v |= mask
    return v


def gen_password(length=12):
    s = "abcdef1234567890-xyzkABCDEFXYZK"
    pw = ''.join(secrets.choice(s) for x in range(length - 1))
    while pw[0] == '-' or not check_password_format(pw):
        pw = ''.join(secrets.choice(s) for x in range(length))
    return pw


def check_password_format(pwd):
    return not (len(pwd) < 8 or re.search('[0-9]', pwd) is None or re.search('[A-Z]', pwd) is None)


def isValidEmail(email):
    if len(email) > 7:
        if "abuse@" in email:
            return False
        if re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) is not None:
            return True
    return False


def isValidPhoneNumber(phone_number):
    # Starts with + then at least 9 numbers follow
    if re.match("^\+[0-9]{8,}$", phone_number) is not None:
        return True
    return False


def create_checksum(code):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZ-'
    c = 0
    for i in range(len(code)):
        c += alphabet.index(code[i]) * (i + 1)
    return alphabet[c % len(alphabet)]


def check_checksum(code):
    try:
        return create_checksum([c for c in code[:-1]]) == code[-1]
    except:
        return False


def generate_easy_id(size=10):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    result = ''.join(secrets.choice(alphabet + '-') for x in range(size - 2))
    result = secrets.choice(alphabet) + result
    result += (create_checksum(result))
    return "".join(result)
