#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing 

import os

#################

# Console colors
W = '\033[1;0m'  # white
R = '\033[1;31m'  # red
G = '\033[1;32m'  # green
O = '\033[1;33m'  # orange
B = '\033[1;34m'  # blue
Y = '\033[1;93m'  # yellow
P = '\033[1;35m'  # purple
C = '\033[1;36m'  # cyan
GR = '\033[1;37m'  # gray
colors = [G, R, B, P, C, O, GR]

info = '{0}[*]{1} '.format(B, W)
query = '{0}[?]{1} '.format(C, W)
error = '{0}[-]{1} '.format(R, W)
good = '{0}[+]{1} '.format(G, W)

headers = {"User-Agent": "autopentesting/V1.0", "Accept": "*/*",
           "Content-type": "application/json", "Connection": "close"}


# 简化一些信息
def print_info(text):
    print(info + text)


def print_query(text):
    print(query + text)


def print_error(text):
    print(error + text)


def print_good(text):
    print(good + text)


def make_directory(directory):
    if not os.path.exists(directory):
        print_good("新建新目录:{0}".format(directory))
        os.makedirs(directory)


def check_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

# check connection

# create
