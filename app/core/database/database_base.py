#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing 
from app.core.database.db_mongo import mongo
from bson import ObjectId


class DatabaseBase:
    def __init__(self):
        self.table = ""

    def find_one(self):
        return mongo[self.table].find_one()

    def find_by_id(self, _id):
        return mongo[self.table].find_one({"_id": ObjectId(str(_id))})

    def get_list(self):
        return mongo[self.table].find().sort("date", -1)

    def get_count(self, query=None):
        return mongo[self.table].find(query).count()

    def delete_by_id(self, _id):
        return mongo[self.table].delete_one({"_id": ObjectId(str(_id))})