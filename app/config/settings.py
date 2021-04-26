#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing
import os
import platform

LOGGER_PATH = os.path.abspath(os.path.dirname(__file__)) + '/../logs/'

current_path = os.path.abspath(os.path.dirname(__file__))

class IcewingConfig(object):
    # Base configuration
    DEBUG = True
    AUTH = True
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8888
    SECRET_KEY = 'B10ySw1nPL8JBo6z'
    AUTH = False
    # Redis configuration
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = "6379"
    REDIS_PASSWORD = ""
    REDIS_DB = 0
    # MongoDB configuration
    MONGO_HOST = "localhost"
    MONGO_PORT = 27017
    MONGO_DB = 'icewing_dev'
    MONGO_USER = ''
    MONGO_PASSWD = ''


# MISC
workdir = ''
plugindir = current_path + "/../plugins/"

if 'Darwin' in platform.system():
    xraypath = plugindir + "xray/xray_darwin_amd64 "
    crawlergopath = plugindir + "crawlergo "
    chromepath = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
    masscanpath = "/usr/local/bin/masscan "
else:
    crawlergopath = plugindir + "crawlergolinux64 "
    chromepath = plugindir + "chromedriver "
    xraypath = plugindir + "xray_linux_amd64"
    masscanpath = "/usr/bin/masscan "

ddkey = "https://oapi.dingtalk.com/robot/send?access_token="

xraylisten = ""
AWVSAPI = ""
subfinder = ""
shodankey = ""
# ysoserial_jar = '/Users/wing/evilwing/pentesting/shirorce/moule/ysoserial.jar'

## DNslog
LOCAL_IP = ''
ROOT_DOMAIN = "redteamwing.com"
PASSWORD = " "
config = IcewingConfig()
