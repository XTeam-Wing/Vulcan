#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing

from app.common.auth.user import DBWingAdmin

def db_init():
    if not DBWingAdmin.find_one():
        DBWingAdmin.add_admin(
            username="wing", password="redteamwing",
            nick="Administrator", email="admin@evilwing.me",
        )

