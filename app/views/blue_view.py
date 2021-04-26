#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing 

from flask import request, Blueprint, render_template


blue_view = Blueprint('blue_views', __name__)


@blue_view.route('/', defaults={'path': ''})
@blue_view.route('/<path:path>')
def index(path):
    return render_template('index.html')
