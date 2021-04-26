#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing 
from app.router import create_app
from app.common.utils.banner import banner

print(banner)
create_app.run(debug=True, port=5000, host="0.0.0.0")

