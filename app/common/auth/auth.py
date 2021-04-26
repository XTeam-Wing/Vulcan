#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : RedTeamWing
# @CreateTime: 2020/5/8 10:20 下午
# @FileName: auth.py
# @Blog：https://redteamwing.com
from flask_httpauth import HTTPBasicAuth
import hashlib

auth = HTTPBasicAuth()

PASSWORD = "Wing666"


def md5(src):
    m2 = hashlib.md5()
    m2.update(src)
    return m2.hexdigest()


API_TOKEN = md5("ded08972cead38d6ed8f485e5b65b4b6" + PASSWORD)


@auth.verify_password
def verify_pw(username, password):
    # print(username, password)
    if username == 'admin' and password == PASSWORD:
        return 'true'
    return None
