from flask import Blueprint


class RegisteringBlueprint(Blueprint):
    config = None
    logger = None
    app = None

    def register(self, app, options, first_registration=False):
        self.app = app
        self.config = app.config
        self.logger = app.logger
        super(RegisteringBlueprint, self).register(app, options, first_registration)
