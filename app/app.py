#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing

from flask import Flask
from flask_cors import CORS
from secrets import token_urlsafe
from app.config.settings import config


def create_app():
    app = Flask(__name__, static_folder="../dist/", static_url_path='', template_folder="../dist")
    app.config.from_object(config)
    # app.config.from_object('app.config.secret')
    app.config['CELERY_BROKER_URL'] = "redis://{}:{}/{}".format(
        app.config.get("REDIS_HOST"), app.config.get("REDIS_PORT"), app.config.get("REDIS_DB"),
    )
    app.config['MONGO_URI'] = "mongodb://{}:{}/{}".format(
        app.config.get("MONGO_HOST"), app.config.get("MONGO_PORT"), app.config.get("MONGO_DB"),
    )

    app.config['SECRET_KEY'] = token_urlsafe()
    # print(app.config)

    # app.register_blueprint(dns_log)
    CORS(app)
    return app


create_app = create_app()
# celerywing = Celery(create_app.name,broker="redis://localhost:6379/0")
# create_app().app_context().push()
