# Flask debug mode
DEBUG = False

API_ENDPOINT = 'https://backend.tggapp.hu:5019/tggapp/api/v1.0'

# Seconds to wait before restarting a failed worker.
BGSERVICE_RESTART_FAILED_SERVICE_WAIT = 5
# Maximum number of a service restart, before bgservice terminates.
BGSERVICE_FAILED_SERVICE_MAX_RESTART_COUNT = 10

MYSQL_DATABASE_HOST = 'localhost'
MYSQL_DATABASE_USER = 'user'
MYSQL_DATABASE_PASSWORD = 'password'
MYSQL_DATABASE_DB = 'tggapp db'

PARSE_FROM_ENVVARS = ""

BGSERVICE_API_USER = ''
BGSERVICE_API_PASSWORD = ''

EPIDEMICIMPORT_DELAY = 1000
EPIDEMICPLAYLIST_DELAY = 1000
EPIDEMICPLAYLIST_WINDOW_FROMHR = 0
EPIDEMICPLAYLIST_WINDOW_TOHR = 5
PLAYLISTCLEANUP_DELAY = 1000
TOKENCLEANUP_DELAY = 1000
FORCE_CONTENTUPDATE_HOUR = 2

EPIDEMIC_IMPORT_CSV = ' .... .csv'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'bgservice.log',
            'when': 'd',
            'interval': 1,
            'backupCount': 0,
            'delay': False,
            'formatter': 'default'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'root': {
        'level': 'INFO',
        # Add 'console' to the handlers for logging to the console as well.
        'handlers': ['file', 'console']
    },
    'loggers': {
        # Log configuration of SQLAlchemy is specified at
        # https://docs.sqlalchemy.org/en/latest/core/engines.html#configuring-logging
        # Default log level is WARN within the entire sqlalchemy namespace.

        # Controls SQL echoing. set to logging.INFO for SQL query output, logging.DEBUG for query + result set output.
        # 'sqlalchemy.engine': {
        #     'level': 'DEBUG'
        # },
        # Our python packages use separate loggers under the 'variance' namespace. Set the log level (and other
        # parameters) for the entire 'variance' namespace here. You can set separate parameters for each logger as well.
        # 'variance': {
        #     'level': 'INFO'
        # },
        # Separate configuration for the deposit check module.
        # 'variance.xchaddress_lookup': {
        #     'level': 'DEBUG'
        # },
        # Kraken module
        # 'variance.xchkraken': {
        #     'level': 'DEBUG'
        # },
    }
}
