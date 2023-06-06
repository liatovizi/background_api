from flask_restplus import Namespace\
    #, fields
from natapp.libs.naterrors import Errors
from functools import wraps
from flask_restx import fields


class RegisteringNamespace(Namespace):
    config = None
    logger = None
    app = None

    class Paginated(list):
        pass

    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)

        self.error_block_400 = self.model(
            'ErrorBlock_400', {
                "code":
                fields.String(description="error code",
                              example="EGEN_badreq_E001",
                              enum=["EGEN_400_E001", "EGEN_http_E001", "EGEN_badreq_E001"]),
                "message":
                fields.String(example="verbose error message", description="verbose error message")
            })
        self.error_block_422 = self.model(
            'ErrorBlock_422', {
                "code": fields.String(
                    description="error code",
                    enum=[""],
                ),
                "message": fields.String(example="verbose error message", description="verbose error message")
            })
        self.error_block_500 = self.model(
            'ErrorBlock_500', {
                "code": fields.String(
                    description="error code", example="EGEN_internal_E001", enum=["EGEN_internal_E001"]),
                "message": fields.String(example="verbose error message", description="verbose error message")
            })
        self.error_block_200 = self.model(
            'ErrorBlock_200', {
                "code": fields.String(description="error code", example="none", enum=["none"]),
                "message": fields.String(example="none", enum=["none"], description="verbose error message")
            })
        self.default_response_200 = self.model(
            'DefaultResponse_200', {
                "status": fields.String(enum=["ok"], required=True, description="status field"),
                "result": fields.Raw(description="endpoint specific payload object", required=True),
                "error": fields.Nested(self.error_block_200, required=True)
            })
        self.default_response_400 = self.model(
            'DefaultResponse_400', {
                "status": fields.String(enum=["error"], required=True, description="status field"),
                "result": fields.Raw(description="endpoint specific payload object", required=True),
                "error": fields.Nested(self.error_block_400, required=True)
            })
        self.default_response_422 = self.model(
            'DefaultResponse_422', {
                "status": fields.String(enum=["error"], required=True, description="status field"),
                "result": fields.Raw(description="endpoint specific payload object", required=True),
                "error": fields.Nested(self.error_block_422, required=True)
            })
        self.default_response_500 = self.model(
            'DefaultResponse_500', {
                "status": fields.String(enum=["error"], required=True, description="status field"),
                "result": fields.Raw(description="endpoint specific payload object", required=True),
                "error": fields.Nested(self.error_block_500, required=True)
            })
        self.default_responses = {
            500: ('internal server error', self.default_response_500),
            400: ('error when preprocessing request', self.default_response_400),
            422: ('unable to process data', self.default_response_422),
            #200: ('success', self.default_response_200)
        }

    def registerapp(self, app):
        self.app = app
        self.config = app.config
        self.logger = app.logger

    def requestdecorator(self,
                         name,
                         responsefields_201=None,
                         responsefields=None,
                         errors=None,
                         jsonfields=None,
                         validate=True,
                         response_200=None,
                         response_201=None,
                         parserparams=None):
        params = {}
        responses = {
            500: ('internal server error', self.default_response_500),
            400: ('error when preprocessing request', self.default_response_400)
        }
        if errors:
            errors = list(map(lambda x: Errors.get_text(x)[0], errors)),
            responses['422'] = (
                'unable to process data',
                self.clone(
                    name + '_422', self.default_response_422, {
                        'error':
                        fields.Nested(
                            self.clone(
                                name + 'Error_422', self.error_block_422,
                                {"code": fields.String(description="error code", example=errors[0], enum=errors)}))
                    }))
        if responsefields == None:
            responsefields = {}
        if response_200 != None:
            responsefields['200'] = response_200
        if response_201 != None:
            responsefields['201'] = response_201
        if responsefields:
            for code, value in responsefields.items():
                if not code in ["200", "201"]:
                    raise Exception(f"Bad status code in request decorator name: {name}, code:{code}")
                responses[code] = (
                    'success',
                    self.clone(
                        name + "_response_" + code, self.default_response_200, {
                            "result":
                                fields.Nested(self.model(name + "_response_" + code + "_paginated_block", {'page': fields.Integer(example=1, min=1, description='page number'), 'per_page': fields.Integer(example=25, min=1, description='items per page'), 'items': fields.Integer(example=111, min=0, description='items total count'), 'data':fields.List(fields.Nested(self.model(name + "_response_" + code + "_block", value[0])))})) \
                                    if isinstance(value, self.Paginated) else ( fields.Nested(self.model(name + "_response_" + code +
                                                     "_block", value)) if not isinstance(value, list) else
                            fields.List(fields.Nested(self.model(name + "_response_" + code + "_block", value[0]))))
                        }))
        if not responsefields:
            responses['200'] = ('success', self.default_response_200)
        params['responses'] = responses
        expect = []
        params['expect'] = expect
        if validate != None:
            params['validate'] = validate or self._validate
        if jsonfields:
            expect.append(self.model(name + '_input_jsonfields', jsonfields))
        parser = None
        if parserparams:
            parser = self.parser()
            parser.bundle_errors = False
            for prm in parserparams:
                parser.add_argument(prm[0], **prm[1])
            expect.append(parser)
        apifun = self.doc(**params)
        if parser:

            def wrapper(func):
                @wraps(func)
                def wrappee(*args, **kwargs):
                    parser.parse_args()
                    return func(*args, **kwargs)

                return apifun(wrappee)

            return wrapper
        return apifun
