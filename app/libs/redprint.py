#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing 

class Redprint:

    def __init__(self,name):
        self.name = name
        # list save多个route
        self.mound = []

    # 路由装饰器
    def route(self,rule,**options):
        def decorator(f):
            self.mound.append((f,rule,options))
            return f
        return decorator
    def register(self,bp,url_prefix=''):
        # if url_prefix == '':
        #     url_prefix = '/' + self.name
        for f,rule,options in self.mound:
            # 取函数名或者endpoint
            endpoint = options.pop('endpoint',f.__name__)
            bp.add_url_rule(url_prefix + rule,endpoint,f, **options)