import os
import sys
import time
import logging
import getopt
from logging.config import dictConfig
from natapp import db
from natapp.libs import natutility
import bgservice
from bgservice.workers import dummy_worker, dummy2_worker, epidemicimport_worker, epidemicplaylist_worker, tokencleanup_worker, playlistcleanup_worker, forceupdate_worker

logger = logging.getLogger()


def configure_logging(config):
    log_config = config.get('LOGGING')

    if log_config is None:
        print('LOGGING is missing from the configuration!')
        sys.exit(1)

    dictConfig(log_config)


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
    if "--version" in sys.argv:
        print(f"bgservice version: {bgservice.__version__}")
        sys.exit(0)

    config = load_config(["bgserviceconfig.py", "instance/bgserviceconfig.py"])
    configure_logging(config)

    logger = logging.getLogger()

    logger.info(f'bgservice started, version: {bgservice.__version__}')

    for key, value in config.items():
        logger.debug(f"CONFIG {key}={value}")

    uri = 'mysql+pymysql://%s:%s@%s/%s' % (config['MYSQL_DATABASE_USER'], config['MYSQL_DATABASE_PASSWORD'],
                                           config['MYSQL_DATABASE_HOST'], config['MYSQL_DATABASE_DB'])
    connection = db.Connection(uri)
    session = connection.new_session()

    if not db.check(session):
        logger.error("Database is not consistent with sqlalchemy db schema. Exiting...")
        sys.exit(-1)

    db.session = session

    if not natutility.get_lock_file():
        logger.error('Unable to acquire a lock. Another instance might be running.')
        sys.exit(1)
    api_url = config['API_ENDPOINT']
    BGSERVICE_API_USER = config['BGSERVICE_API_USER']
    BGSERVICE_API_PASSWORD = config['BGSERVICE_API_PASSWORD']

    services = []
    restartwait = 5
    maxrestart = 0
    if 'BGSERVICE_RESTART_FAILED_SERVICE_WAIT' in config:
        restartwait = config['BGSERVICE_RESTART_FAILED_SERVICE_WAIT']
    if 'BGSERVICE_FAILED_SERVICE_MAX_RESTART_COUNT' in config:
        maxrestart = config['BGSERVICE_FAILED_SERVICE_MAX_RESTART_COUNT']

    options, remainder = getopt.getopt(sys.argv[1:], 's:c:w:', ['services=', 'resart-count=', 'resart-wait='])
    for opt, arg in options:
        if opt in ('-s', '--services'):
            services = arg.split(",")
        if opt in ('-c', '--restart-count'):
            maxrestart = int(arg)
        if opt in ('-w', '--restart-wait'):
            restartwait = int(arg)

    workers = []

    if 'dummy' in services:
        workers.append(dummy_worker.DummyWorker)
    if 'dummy2' in services:
        workers.append(dummy2_worker.Dummy2Worker)
    if not services or 'epidemicimport' in services:
        workers.append(epidemicimport_worker.EpidemicimportWorker)
    if not services or 'epidemicplaylist' in services:
        workers.append(epidemicplaylist_worker.EpidemicplaylistWorker)
    if not services or 'tokencleanup' in services:
        workers.append(tokencleanup_worker.TokencleanupWorker)
    if not services or 'playlistcleanup' in services:
        workers.append(playlistcleanup_worker.PlaylistcleanupWorker)
    if not services or 'forceupdate' in services:
        workers.append(forceupdate_worker.ForceUpdateWorker)

    if len(workers) == 0:
        logger.error(f"No valid worker services specified. Exiting...")
        sys.exit(0)

    workerthreads = []
    for x in workers:
        workerthreads.append(x.create(config))

    restartcnt = [0] * len(workerthreads)

    for wrkr in workerthreads:
        wrkr.setDaemon(True)
        wrkr.start()

    while True:
        for i in range(len(workerthreads)):
            if not workerthreads[i].isAlive():
                restartcnt[i] += 1
                if restartcnt[i] > maxrestart:
                    logger.error(
                        f"Worker thread '{workerthreads[i].getName()}' died unexpectedly more than {maxrestart} times. Exiting..."
                    )
                    sys.exit(1)
                else:
                    logger.warning(
                        f"Worker thread '{workerthreads[i].getName()}' died unexpectedly {restartcnt[i]} times. Restarting in {restartwait} seconds..."
                    )
                    time.sleep(restartwait)
                    logger.warning(f"Restarting worker thread '{workerthreads[i].getName()}'...")
                    workerthreads[i] = workers[i].create(config)
                    workerthreads[i].setDaemon(True)
                    workerthreads[i].start()

        time.sleep(1)
