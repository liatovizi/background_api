# Flask debug mode
DEBUG = False

LAYOUT_JSON_FILE = 'static/layout.json'
LAYOUT_JSON_FILE_CC = 'static/layout_cc.json'

DISABLE_REGISTRATION = False
DISABLE_FORGOTPASSWORD = False

CORS_ENABLED = True
CORS_DOMAINS = ""

SSL_CERTIFICATE = '/etc/letsencrypt/.../fullchain.pem'
SSL_PRIVATE_KEY = '/etc/letsencrypt/.../privkey.pem'

API_ENDPOINT = 'http://localhost:5019/tggapp/api/v1.0'
VERIFYACCOUNT_URL = 'http://localhost:5019/tggapp/api/v1.0/public/verifyaccount?token='
PWRESET_URL_BASE = 'http://localhost:5019/tggapp/api/v1.0/public/resetpassword?token='

SUPPORTED_LANGUAGES = ["en", "hu"]

PASSWORD_HASH_DEFAULT_ROUNDS = 4

PARSE_FROM_ENVVARS = ["TGG_APPLICATION_DEVICELOG_DIR"]

TGG_APPLICATION_PSK = "test123"
TGG_APPLICATION_DEVICELOG_DIR = ""

#
# The following parameters must be updated in the instance config
#

MYSQL_DATABASE_HOST = 'mysql'
MYSQL_DATABASE_USER = 'root'
MYSQL_DATABASE_PASSWORD = 'password'
MYSQL_DATABASE_DB = 'tggapp_test'

SMTP_HOST = 'localhost'
SMTP_PORT = '1025'
SMTP_USER = 'username'
SMTP_PASSWORD = 'pw'
SMTP_SENDER = 'xxx@yyy.zzz'
SMTP_SENDERNAME = 'Sender Name'
SMTP_TESTMODE = True

BGSERVICE_API_USER = 'bgservice'
BGSERVICE_API_PASSWORD = 'secretpassword123'

# Warning: Flask profiler does not work in a multithreaded environment using the 'sqlite' storage engine.
# Try to change the storage setting to the following to overcome the problems:
# "engine": "sqlalchemy",
# "db_url": "sqlite:///flask_profiler.db"
#
ENABLE_PROFILER = False

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
            'filename': 'tggapp.log',
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
        #'sqlalchemy.engine': {
        #    'level': 'DEBUG'
        #},

        # This configures the logger available through 'app.logger'.
        'flask.app': {
            'level': 'INFO'
        }
    }
}
