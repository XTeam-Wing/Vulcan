#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing 
from flask_restful import Api
from app.app import create_app
from app.api.demo.demo import HelloWorld
from app.api.httplog.httplog import Httplog
from app.api.dnslog.dnslog import Dnslog
from app.api.httplog.log import Log, VerifyHttp
from app.api.poc.pocupload import PocManage
from app.api.poc.pocscan import PocScan, PocVuln, FreqScan
from app.api.common.subdomain import subDomain, SubdomainList, FindSubTask, NewTask, SubdomainResultExport
from app.api.vulnscan.vulnscan import Vuln
from app.api.vulnscan.vulnlist import VulnList, Assetdata, VulnDetail
from migration.db_init import db_init
from app.api.webhook.dd import webhook

from app.api.dnslog.dnslog import dns_log
from app.views.blue_view import blue_view

create_app.register_blueprint(dns_log)
create_app.register_blueprint(blue_view)
api = Api(create_app)

api.add_resource(HelloWorld, '/api/hello')
api.add_resource(Httplog, "/api/httplog")
api.add_resource(Log, '/log/<id>')
api.add_resource(VerifyHttp, '/verify/<pid>')


api.add_resource(PocManage, '/scanner/pocmanage')
api.add_resource(PocScan, '/scanner/pocscan')
api.add_resource(PocVuln, '/scanner/pocvuln')
api.add_resource(FreqScan, '/scanner/freqscan')


api.add_resource(subDomain, '/api/common/subdomain')
api.add_resource(NewTask, '/api/common/newtask')
api.add_resource(SubdomainList, '/api/common/subdomainlist')
api.add_resource(SubdomainResultExport, '/api/common/subdomainexport/<pid>')
api.add_resource(FindSubTask, '/api/common/subtaskstate')

api.add_resource(Vuln, '/api/vulnscan')
api.add_resource(VulnList, '/api/common/vulnlist')
api.add_resource(Assetdata, '/api/common/assetdata')
api.add_resource(VulnDetail, '/api/common/vulndetail')

api.add_resource(webhook, '/webhook')

api.add_resource(Dnslog, '/api/dnslog')
db_init()
