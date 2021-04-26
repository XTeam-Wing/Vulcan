#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing
from app.core.database.database_base import DatabaseBase
from app.core.database.db_mongo import Subdomain, mongo, VulnScan, LinksDB_V1, VulnDB
from app.core.database.dberror import DatabaseError
import time
from bson import ObjectId
from app.common.utils.logger import logger


class _DBSubdomain(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = Subdomain

    def add(self, domain, title, url, server, project, company_name, taskid, port=None, ip=None, icp=None):
        if domain:
            insert_id = mongo[self.table].insert_one({
                "taskid": str(taskid), "domain": domain.strip(), "url": url, "ip": str(ip), "title": str(title),
                "server": str(server), "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "project": str(project), "company_name": str(company_name), "port": str(port), "icp": str(icp)
            }).inserted_id
            print(insert_id)
            return str(insert_id)
        else:
            logger.warning('入库error')
            raise DatabaseError("invalid data")

    def update_by_id(self, tid, data):
        return mongo[self.table].update_one(
            {"_id": ObjectId(tid)}, {"$set": data}
        )

    # def update(self, taskid, data):
    #     return mongo[self.table].update_many({"taskid": taskid}, {"$set": data})
    def getsubdomain_count(self, query=None):
        return mongo[self.table].find(query).count()

    def get_list(self, query=None, data_filter=None):
        keyword = data_filter.lower()
        return mongo[self.table].find({
            "$or": [
                {"domain": {'$regex': keyword}}, {"server": {'$regex': keyword}},
                {"target": {'$regex': keyword}}, {"ip": {'$regex': keyword}},
                {"company_name": {'$regex': keyword}}, {"title": {'$regex': keyword}},
                {"taskid": {'$regex': keyword}}, {"port": {'$regex': keyword}}
            ]
        })

    def get_list_by_id(self, tid):
        return mongo[self.table].find({"taskid": str(tid)})


class _VulnScanDB(DatabaseBase):
    def __init__(self):
        self.table = VulnScan

    def AddVulScan(self, projectid, host, ip, portserver, company_name):
        insert_id = mongo[self.table].insert_one({
            "projectid": projectid,
            "host": host,
            "ip": ip,
            "portserver": portserver,
            "company_name": company_name,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }).inserted_id
        return insert_id


class _LinksDB(DatabaseBase):
    def __init__(self):
        self.table = LinksDB_V1

    def AddLinks(self, projectid, host, port, links):
        insert_id = mongo[self.table].insert_one({
            "projectid": projectid,
            "host": host,
            "port": port,
            "links": links,
        }).inserted_id
        return insert_id


class _VulnDB(DatabaseBase):
    def __init__(self):
        self.table = VulnDB

    def AddVuln(self, host, url, payload, plugin, vulntype, time):
        insert_id = mongo[self.table].insert_one({
            "host": host,
            "url": url,
            "payload": payload,
            "plugin": plugin,
            "vulntype": vulntype,
            "time": time
        }).inserted_id
        return insert_id

    def getVulnList(self):
        query = '''
        .aggregate
        ([ 
{$lookup: { 
     from: 'VulnDB', 
     localField: 'host', 
     foreignField: 'host', 
     as: 'vulndetail' 
     }}, 
         {$lookup: { 
     from: 'LinksDB', 
     localField: 'host', 
     foreignField: 'host', 
     as: 'linkdetail' 
     }}, 

])
        '''
        # print(query)
        return mongo[VulnScan].aggregate([{'$lookup': {'from': 'VulnDB', 'localField': 'host',
                                                       'foreignField': 'host',
                                                       'as': 'vulndetail'
                                                       }},
                                          {'$lookup': {
                                              'from': 'LinksDB',
                                              'localField': 'host',
                                              'foreignField': 'host',
                                              'as': 'linkdetail'
                                          }},
                                          ])

    def getvulncount(self):
        res = mongo[self.table].aggregate([{'$lookup': {'from': 'VulnDB', 'localField': 'host',
                                                        'foreignField': 'host',
                                                        'as': 'vulndetail'
                                                        }},
                                           {'$lookup': {
                                               'from': 'LinksDB',
                                               'localField': 'host',
                                               'foreignField': 'host',
                                               'as': 'linkdetail'
                                           }},
                                           {
                                               "$group": {
                                                   '_id': '', 'count': {'$sum': 1}
                                               }
                                           }
                                           ])

        return res


class _HTTPLOG_DB(DatabaseBase):
    def __init__(self):
        self.table = "HTTPLOG"

    def add(self, ip, referrer, data):
        if ip and data and referrer:
            inserted_id = mongo[self.table].insert_one({
                "ip": ip.strip(), "data": data, "referrer": referrer,
                "date": int(time.time())
            }).inserted_id
            return str(inserted_id)
        else:
            logger.warning("http request log insert failed: invalid data")
            raise DatabaseError("invalid data")

    def verify(self, verifydata):
        return mongo[self.table].find_one({"_id": ObjectId(verifydata)})

    def delete_by_id(self, id):
        return mongo[self.table].delete_one({"_id": ObjectId(str(id))})


class _TaskDB(DatabaseBase):
    def __init__(self):
        self.table = "taskDB"

    def add(self, taskid, project, rootdomain, subdomain_count, portcount, flag, freq):
        inserted_id = mongo[self.table].insert_one({
            "taskid": taskid, "project": str(project), "rootdomain": str(rootdomain),
            "subdomain_count": int(subdomain_count), "freq": freq,
            "portcount": int(portcount), "flag": int(flag),
            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}).inserted_id
        return str(inserted_id)

    def update(self, taskid, data):
        return mongo[self.table].update_many({"taskid": taskid}, {"$set": data})

    def find_all(self):
        return mongo[self.table].find({})

    def delete_by_id(self, _id):
        return mongo[self.table].delete_one({"_id": ObjectId(str(_id))})

    def get_by_id(self, _id):
        return mongo[self.table].find({"taskid": str(_id)})

    def get_list(self, query=None, data_filter=None):
        return mongo[self.table].find(query, data_filter)

    def check_by_name(self, name):
        return mongo[self.table].find({"project": str(name)})


class _PocsuiteDB(DatabaseBase):
    def __init__(self):
        self.table = "PocsuiteDB"
        self.localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def add(self, name, poc_content, filename, app=None, vulntype=None, desc=None, author=None):
        if name and poc_content:
            inserted_id = mongo[self.table].insert_one({
                "name": name.strip(), "poc_content": poc_content, "app": app,
                "vulntype": vulntype, "filename": filename,
                "date": self.localtime, "desc": desc,
                "author": author
            }).inserted_id
            return str(inserted_id)
        else:
            raise DatabaseError("upload data error!")

    def filter_by_id(self, pid):
        return mongo[self.table].find({"_id": ObjectId(pid)})

    def filter_by_keywords(self, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "$or": [
                {"name": {'$regex': keyword}}, {"filename": {'$regex': keyword}}
            ]
        })

    def get_list(self, query=None, data_filter=None):
        return mongo[self.table].find(query, data_filter)

    def get_detail_by_id(self, _id):
        return mongo[self.table].find_one({"_id": ObjectId(str(_id))})

    def delete_by_id(self, _id):
        return mongo[self.table].delete_one({"_id": ObjectId(str(_id))})


class _PocscanTask(DatabaseBase):
    def __init__(self):
        self.table = "PocscanTask"
        self.localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def add(self, name, target, poc, thread, frequency):
        if name and target and poc and thread:
            inserted_id = mongo[self.table].insert_one({
                "name": name.strip(), "target": target, "poc": poc,
                "thread": thread, "frequency": int(frequency),
                "date": self.localtime, "end_date": 0,
                "status": "Waiting", "vul_count": 0,
            }).inserted_id
            return str(inserted_id)
        else:
            raise DatabaseError("invalid data")

    def get_list(self, query=None, data_filter=None):
        return mongo[self.table].find(query, data_filter)

    def find_by_id(self, _id):
        return mongo[self.table].find_one({"_id": ObjectId(str(_id))})

    def update_by_id(self, tid, data):
        return mongo[self.table].update_one(
            {"_id": ObjectId(tid)}, {"$set": data}
        )

    def delete_by_id(self, _id):
        return mongo[self.table].delete_one({"_id": ObjectId(str(_id))})


class _PocsuiteVul(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = "PocsuiteVuln"
        self.localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def add(self, taskid, poc, task_name, poc_name, status, target, app, result=""):
        if taskid and poc and task_name and poc_name and status and target and app:
            inserted_id = mongo[self.table].insert_one({
                "taskid": taskid, "poc": poc, "task_name": task_name,
                "poc_name": poc_name, "status": status,
                "target": target, "app": app, "result": result,
                "date": self.localtime,
            }).inserted_id
            return str(inserted_id)
        else:
            logger.warning("pocsuite scan result insert failed: invalid data")
            raise DatabaseError("invalid data")

    def get_list(self, query=None, data_filter=None):
        return mongo[self.table].find(query, data_filter)

    def delete_by_id(self, _id):
        return mongo[self.table].delete_one({"_id": ObjectId(str(_id))})

    def delete_by_tid(self, tid):
        return mongo[self.table].delete_many({"taskid": str(tid)})


HTTPLOG_DB = _HTTPLOG_DB()
DBSubdomain = _DBSubdomain()
VulnScanDB = _VulnScanDB()
LinksDB = _LinksDB()
VulnDB = _VulnDB()
TaskDB = _TaskDB()
PocsuiteDB = _PocsuiteDB()
PocscanTask = _PocscanTask()
PocsuiteVuln = _PocsuiteVul()
