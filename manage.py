from argparse import ArgumentParser
import os
import sys
from copy import copy

from migrate.versioning.api import version_control, upgrade, downgrade, db_version, version
from sqlalchemy.engine.url import make_url
import sqlalchemy as sa


def db_url_from_config(config):
    return f'mysql+pymysql://{config["MYSQL_DATABASE_USER"]}:{config["MYSQL_DATABASE_PASSWORD"]}@' \
           f'{config["MYSQL_DATABASE_HOST"]}/{config["MYSQL_DATABASE_DB"]}'


def init_db(db_url):
    print('Installing version control...')
    version_control(db_url, "db-migration/nat_repository")
    print('Applying migration scripts...')
    upgrade(db_url, "db-migration/nat_repository")


def drop_db(config):
    url = copy(make_url(db_url_from_config(config)))
    database = url.database
    url.database = None

    print(f'Dropping DB "{database}"...')

    engine = sa.create_engine(url)

    if not is_db_exists(engine, database):
        print('Database not exists.')
        exit(1)

    text = f'DROP DATABASE IF EXISTS {database}'
    conn_resource = engine.execute(text)

    if conn_resource is not None:
        conn_resource.close()
    engine.dispose()


def is_db_exists(engine, db):
    text = f'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = "{db}"'

    result_proxy = engine.execute(text)

    if result_proxy.first():
        ret = True
    else:
        ret = False

    if result_proxy is not None:
        result_proxy.close()

    return ret


def create_db(config):
    db_url = db_url_from_config(config)

    url = copy(make_url(db_url))
    database = url.database
    url.database = None

    engine = sa.create_engine(url)

    print(f'Creating DB "{database}"...')

    if is_db_exists(engine, database):
        print('Database already exists. Drop the database by "drop-db" if you want to re-create it.')
        exit(1)

    text = f'CREATE DATABASE {database} CHARACTER SET = utf8mb4 COLLATE utf8mb4_unicode_ci'
    result_proxy = engine.execute(text)

    if result_proxy is not None:
        result_proxy.close()
    engine.dispose()

    init_db(db_url)


def upgrade_db(config):
    current_version = db_version(db_url_from_config(config), "db-migration/nat_repository")
    max_version = version("db-migration/nat_repository")

    print(f'Upgrading DB from {current_version} to {max_version}')

    upgrade(db_url_from_config(config), "db-migration/nat_repository")


def downgrade_db(config, version):
    current_version = db_version(db_url_from_config(config), "db-migration/nat_repository")

    print(f'Downgrading DB from {current_version} to {version}')

    downgrade(db_url_from_config(config), "db-migration/nat_repository", version)


def load_config(configfiles):
    result = dict()
    for f in configfiles:
        pf = os.path.splitext(os.path.basename(f))[0]
        d = os.path.dirname(f)
        sys.path.insert(0, d)
        m = __import__(pf)
        sys.path.remove(d)
        for k, v in m.__dict__.items():
            if not k.startswith("__") or not k.endswith("__"):
                result[k] = v
        del sys.modules[pf]

    return result


if __name__ == '__main__':
    commands = {
        'create-db': (create_db, 0, 'Creates a new database and initializes it by applying the migrations.'),
        'upgrade-db': (upgrade_db, 0, 'Upgrades the DB to the latest version by applying the migration scripts.'),
        'downgrade-db': (downgrade_db, 1, 'Downgrades the DB to the specified version. Parameters: version'),
        'drop-db': (drop_db, 0, 'Drops the DB.')
    }

    parser = ArgumentParser()
    parser.add_argument('command', choices=commands.keys())
    parser.add_argument('parameters', nargs='*')
    # parser.add_argument('-y', action='store_true', help='Confirm all actions automatically. '
    #                                                     'Useful for automated executions.')

    args = parser.parse_args()

    command = commands[args.command]
    if len(args.parameters) != command[1]:
        print(f'Invalid arguments to command! Usage:', command[2])
        exit(1)

    config = load_config(['config.py', 'instance/config.py'])
    #print(config)

    command[0](config, *args.parameters)
