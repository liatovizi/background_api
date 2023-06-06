# Import base modules
import sys

# Import flask modules
from flask import Flask, jsonify, url_for, request
from flask_restplus import Api
from flask_restplus.errors import RestError, ValidationError
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException, BadRequest
import flask_profiler

# Import

from natapp.response import RESP_OK, RESP_OK_201
from natapp.libs import naterrors
import natapp
from natapp import dbbase
from natapp import db as dbsession
from natapp.configer import configure_logging, init_profiler_config
from flask import Blueprint
from natapp.users import auth as users_auth
from natapp.libs import natbgservice as bgservicelib
#from flask_restplus import Namespace, Resource, fields, reqparse
from flask_restx import Namespace, Resource, fields, reqparse
from jsonschema import FormatChecker
import ujson
import os


def register_models(app):
    import natapp.users.models
    import natapp.nat.models


def register_blueprints(app):
    """register all blueprints for application
    """
    from natapp.users.views import user
    app.register_blueprint(user)

    from natapp.nat.views import nat
    app.register_blueprint(nat)

    bp = Blueprint('natapp', __name__)

    api = Api(app=bp,
              doc="/docs",
              title="TGG application backend API",
              version="1.0",
              authorizations=users_auth.authorizations,
              format_checker=FormatChecker())

    @api.errorhandler(Exception)
    def default_error_handler(error):
        raise error  #Exception("Error in flask-restplus request handling") from error

    from natapp.users.views import api as user_ns

    api.add_namespace(user_ns, path="/")

    from natapp.nat.views import api as nat_ns

    api.add_namespace(nat_ns, path="/")

    app.register_blueprint(bp, url_prefix="/tggapp/api/v1.0")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_folder='../static')
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

    if "--version" in sys.argv:
        print(f"xchgapp version: {xchgapp.__version__}")
        sys.exit(0)

    # Load default config from config.py
    app.config.from_object('config')

    if test_config is None:
        # Load instance specific config from instance/config.py.
        # Note that the instance folder is not under version control.
        app.config.from_pyfile('config.py', True)
    else:
        # Load the test config
        app.config.update(test_config)

    if "PARSE_FROM_ENVVARS" in app.config and app.config["PARSE_FROM_ENVVARS"] is not None and app.config[
            "PARSE_FROM_ENVVARS"] != []:
        for confname in app.config["PARSE_FROM_ENVVARS"]:
            app.config[confname] = os.environ.get(confname, default=app.config.get(confname, None))

    configure_logging(app)

    app.logger.info(f'APP started, version: {natapp.__version__}')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s' % (
        app.config['MYSQL_DATABASE_USER'], app.config['MYSQL_DATABASE_PASSWORD'], app.config['MYSQL_DATABASE_HOST'],
        app.config['MYSQL_DATABASE_DB'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    register_models(app)

    app.db = SQLAlchemy(app, model_class=dbbase.Model)

    if not dbsession.check_version(app):
        sys.exit(-1)
    if not dbsession.check(app.db.session):
        app.logger.error("Database is not consistent with sqlalchemy db schema. Exiting...")
        sys.exit(-1)

    init_profiler_config(app)

    register_blueprints(app)

    with app.app_context():
        bgservicelib.init_bgservice_user(app, app.db.session)

    @app.errorhandler(400)
    def custom400(error):
        app.logger.error(error)
        app.logger.error(type(error))
        app.logger.error(dir(error))
        response = ""
        errdesc = naterrors.Errors.get_text(naterrors.Errors.EGEN_400_E001)
        # errdesc = naterrors.Errors.get_text(naterrors.Errors.EGEN_badreq_E001)
        response = jsonify({'status': 'error', 'result': {}, 'error': {'code': errdesc[0], 'message': errdesc[1]}})
        return response, 400

    @app.errorhandler(404)
    def custom404(error):
        errdesc = naterrors.Errors.get_text(naterrors.Errors.EGEN_404_E001)
        response = jsonify({'status': 'error', 'result': {}, 'error': {'code': errdesc[0], 'message': errdesc[1]}})
        return response, 404

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        app.logger.exception(error)
        errdesc = naterrors.Errors.get_text(naterrors.Errors.EGEN_http_E001)
        response = jsonify({'status': 'error', 'result': {}, 'error': {'code': errdesc[0], 'message': errdesc[1]}})
        return response

    @app.errorhandler(BadRequest)
    def handle_badrequest_exception(error):
        #app.logger.error(dir(error))
        #for i in [a for a in dir(error) if not a.startswith('__') and not callable(getattr(error,a))]:
        #    app.logger.error(f"{i}: {getattr(error,i)}")
        if error:
            if hasattr(error, 'data') and error.data['message'] == "Input payload validation failed":
                errdesc = naterrors.Errors.get_text(naterrors.Errors.EGEN_badreq_E001)
                return jsonify({
                    'status': 'error',
                    'result': {},
                    'error': {
                        'code': errdesc[0],
                        # TODO remove the appended error part in the next line after development is done so we won't leak info
                        'message': errdesc[1] + ' - ' + str(error.data)
                    }
                }), 422
            elif hasattr(
                    error, 'description'
            ) and error.description == "The browser (or proxy) sent a request that this server could not understand":
                app.logger.exception(error)
                pass
        else:
            app.logger.exception(error)
        errdesc = naterrors.Errors.get_text(naterrors.Errors.EGEN_400_E001)
        return jsonify({'status': 'error', 'result': {}, 'error': {'code': errdesc[0], 'message': errdesc[1]}}), 400

    @app.errorhandler(Exception)
    def handle_each_exception(error):
        # app.logger.error(f"Exception raised: {error}, return server error\n"+str(traceback.format_tb(error.__traceback__)))
        app.logger.error('Exception raised during processing of the last request')
        app.logger.exception(error)
        errdesc = naterrors.Errors.get_text(naterrors.Errors.EGEN_internal_E001)
        response = jsonify({"status": "error", "data": None, 'error': {'code': errdesc[0], 'message': errdesc[1]}})
        return response, 500

    ###@app.after_request
    def after(response):
        # todo with response
        _x_fwd_to = "N/A"
        _cf_conn_ip = "N/A"
        try:
            _x_fwd_to = request.headers.get('X-Forwarded-For')
            _cf_conn_ip = request.headers.get('CF-Connecting-IP')
        except:
            pass

        app.logger.info(f'{response.status} {_x_fwd_to} {_cf_conn_ip}')
        app.logger.debug(f'{response.headers}')
        app.logger.debug(f'{response.get_data()}')
        return response

    ### TODO try to fix this so empty post bodies will work
    ###@app.before_request
    def handle_post_with_empty_body():
        """This is a workaround to the bug described at
        https://github.com/noirbizarre/flask-restplus/issues/84"""
        ctlen = int(request.headers.environ.get('CONTENT_LENGTH', 0))
        if ctlen == 0:
            request.headers.environ['CONTENT_TYPE'] = None

    @app.after_request
    def apply_caching(response):
        if "Origin" in request.headers:
            if app.config.get("CORS_ENABLED", False):
                r = request.headers["Origin"] if request.headers["Origin"] in app.config.get("CORS_DOMAINS",
                                                                                             "").split(" ") else "null"
            else:
                r = request.headers["Origin"]
        else:
            r = "*"
        response.headers["Access-Control-Allow-Origin"] = r
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "content-type, authorization, doctype"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS, GET, HEAD, PUT, DELETE"
        return response

    if 'flask_profiler' in app.config:
        flask_profiler.init_app(app)

    return app
