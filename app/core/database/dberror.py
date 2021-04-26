#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author:RedTeam@Wing 

class DatabaseError(Exception):
    def __init__(self, error):
        super().__init__(self)
        self.error = error

    def __str__(self):
        return self.error