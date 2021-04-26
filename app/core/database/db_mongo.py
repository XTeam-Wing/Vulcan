#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing
from app.app import create_app
from flask_pymongo import PyMongo

# create_app.config.update(
#     MONGO_HOST='localhost',
#     MONGO_PORT=1111,
#     MONGO_USERNAME='',
#     MONGO_PASSWORD='',
#     MONGO_DBNAME='icewing_dev'
# )

mongo = PyMongo(create_app).db

Subdomain = "Subdomain"
Admin = "Ice_Wing_Admin_v1"
VulnScan = "VulnScan"
LinksDB_V1 = "LinksDB"
VulnDB = "VulnDB"
