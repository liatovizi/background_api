import sys
from logging.config import dictConfig


def configure_logging(app):
    log_config = app.config.get('LOGGING')

    if log_config is None:
        print('LOGGING is missing from the configuration!')
        sys.exit(1)

    dictConfig(log_config)


def init_profiler_config(app):
    if 'ENABLE_PROFILER' not in app.config or not app.config['ENABLE_PROFILER']:
        return

    if 'PROFILER_USER' not in app.config or 'PROFILER_PASSWORD' not in app.config:
        raise ValueError('PROFILER_USER and PROFILER_PASSWORD must be configured in config.py!')

    app.config["flask_profiler"] = {
        "enabled": True,
        "storage": {
            "engine": "sqlite"
        },
        "basicAuth": {
            "enabled": True,
            "username": app.config['PROFILER_USER'],
            "password": app.config['PROFILER_PASSWORD']
        },
        "ignore": ["^/static/.*"]
    }
