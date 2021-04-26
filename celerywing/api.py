#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing


# try:
from celerywing.tasks import Portscan
from celerywing.tasks import Crawlscan
from celerywing.tasks import SubdomainScan
from app.common.utils.utils import *


def api_portscan(hosts, ports, projectid, threads):
    print(hosts, ports, projectid, threads)
    hostList = hosts.split(",")
    for host in hostList:
        Portscan.apply_async(args=[host, ports, projectid, threads])
    return True


def api_Crawlscan(hosts, ports, projectid):
    hostList = hosts.split(",")
    for host in hostList:
        Crawlscan.apply_async(args=[host, ports, projectid])
    return True


def api_SubdomainScan(domain, project, freq):
    SubdomainScan.apply_async(args=[domain, project, freq])
    return True


if __name__ == '__main__':
    # api_portscan(hosts="127.0.0.1,127.0.0.1", ports="8000,8080",  projectid=1231223,threads=10,)
    Crawlscan(host="http://127.0.0.1:1111/", ports="8080")
