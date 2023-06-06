from functools import wraps
import traceback
from flask import request, jsonify, current_app
from natapp.response import *
from natapp import db
from natapp.libs.naterrors import Errors


def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


def fmt_response(response, errcode=None):
    if errcode is not None:
        err_code_text = Errors.get_text(errcode)[0]
        err_message = Errors.get_text(errcode)[1]
        return {'status': 'error', 'result': {}, 'error': {'code': err_code_text, 'message': err_message}}
    else:
        return {'status': 'ok', 'result': response, 'error': {'code': 'none', 'message': 'none'}}


#@parametrized
#def fmt_json_response(func, logger):
def fmt_json_response(func):
    @wraps(func)
    def json_wrap(*args, **kwargs):
        endurl = request.path.rsplit('/', 1)[-1]
        try:
            error_val, value, = func(*args, **kwargs)
        except Exception as ex:  #db.XCHGAppDbException as ex:
            current_app.logger.error(
                f"Exception `{ex}` raised during call API element `{endurl}`. Trace: {traceback.format_tb(ex.__traceback__)}"
            )
            error_val = RESP_ERR
            value = Errors.EGEN_dbresp_E001
        if error_val == RESP_ERR:
            _r = request.get_data()
            if value is None:
                value = Errors.EGEN_unspec_E001
            try:
                # TODO limit the displayed request size to avoid huge log messages (e.g. error of file upload)
                current_app.logger.debug(f"Error: URL='{endurl}', Error='{Errors.get_text(value)}': `{_r}`")
            except:
                pass

            statuscode = 422
            if len(Errors.get_text(value)) == 3:
                statuscode = Errors.get_text(value)[2]
            return jsonify(fmt_response({}, errcode=value)), statuscode

        if error_val == RESP_OK_201:
            return jsonify(fmt_response(value)), 201
        return jsonify(fmt_response(value)), 200

    return json_wrap


def autocommit(func):
    @wraps(func)
    def commit_wrap(*args, **kwargs):
        error_val, value, = func(*args, **kwargs)
        if error_val in (RESP_OK, RESP_OK_201):
            db.session.commit()
        else:
            db.session.rollback()
        return error_val, value

    return commit_wrap


def fmt_json_response_dict(func):
    @wraps(func)
    def json_wrap(*args, **kwargs):
        endurl = request.path.rsplit('/', 1)[-1]
        try:
            error_val, value, = func(*args, **kwargs)
        except Exception as ex:  #db.XCHGAppDbException as ex:
            current_app.logger.error(
                f"Exception `{ex}` raised during call API element `{endurl}`. Trace: {traceback.format_tb(ex.__traceback__)}"
            )
            error_val = RESP_ERR
            value = Errors.EGEN_dbresp_E001
        if error_val == RESP_ERR:
            _r = request.get_data()
            if value is None:
                value = Errors.EGEN_unspec_E001
            try:
                # TODO limit the displayed request size to avoid huge log messages (e.g. error of file upload)
                current_app.logger.debug(f"Error: URL='{endurl}', Error='{Errors.get_text(value)}': `{_r}`")
            except:
                pass

            statuscode = 422
            if len(Errors.get_text(value)) == 3:
                statuscode = Errors.get_text(value)[2]
            return (fmt_response({}, errcode=value)), statuscode

        if error_val == RESP_OK_201:
            return fmt_response(value), 201
        return (fmt_response(value)), 200

    return json_wrap


class req_method_decorator(object):
    def __init__(self, *pargs, autocommit=True, session=None):
        self.pargs = pargs
        self.autocommit = autocommit
        self.session = db.session
        if session:
            self.session = session

    def __call__(self, req_method):
        decorator_self = self

        @wraps(req_method)
        def wrappee(*args, **kwargs):
            current_app.logger.info(
                "req_method2.start %s %s %s %s" % (req_method.__name__, decorator_self.pargs, args, kwargs))

            method_params = {}

            if len(self.pargs):
                try:
                    if not request.json:
                        return RESP_ERR, Errors.EGEN_badreq_E001
                except:
                    return RESP_ERR, Errors.EGEN_parserr_E001
                try:
                    for p in decorator_self.pargs:
                        method_params[p] = request.json[p]
                except (KeyError, ValueError):
                    return RESP_ERR, Errors.EGEN_badreq_E001

            dbsession = self.session

            #try:
            ret = req_method(*args, dbsession, **{**method_params, **kwargs})
            ret_type, value = ret
            #except ValueError as e:
            #    app.logger.error(f'{req_method.__name__} exception: {e}')
            #    session.rollback()
            #    return RESP_ERR, Errors.EGEN_dbresp_E001

            if self.autocommit and (ret_type == RESP_OK or ret_type == RESP_OK_201):
                self.session.commit()

            current_app.logger.info(
                "req_method2.end %s %s %s %s" % (req_method.__name__, decorator_self.pargs, args, kwargs))
            return ret

        return wrappee
