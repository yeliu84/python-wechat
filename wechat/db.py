# -*- coding: utf-8 -*-

"""
wechat.db
---------

This module defines ``DB`` which provides common operations to the wechat
database.
"""

import os

from sqlalchemy import create_engine, MetaData, Table

class DB:
    def __init__(self, mmdb, auto_connect=True):
        self.engine = create_engine('sqlite:///{}'.format(
            os.path.abspath(mmdb)))
        self.meta = MetaData(bind=self.engine)
        self.conn = None
        if auto_connect:
            self.connect()

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = self.engine.connect()

    def close(self):
        if self.conn is not None and not self.conn.closed:
            self.conn.close()

    def reflect(self, tblname):
        return Table(tblname, self.meta, autoload=True)
