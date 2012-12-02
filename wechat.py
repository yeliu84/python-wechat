# -*- coding: utf-8 -*-

"""
wechat
------

This module provides interfaces to various parts of the WeChat database.
"""

__version__ = '0.0.1'
__ver__ = (0, 0, 1)
__author__ = 'Ye Liu'
__license__ = 'BSD'
__copyright__ = 'Copyright (c) 2012 Ye Liu'

import os

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, and_, func

TBL_MASTER_NAME = 'sqlite_master'
TBL_CHAT_PATTERN = 'Chat_%'

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

class Conversation:
    MSG_TYPES = {
        'TEXT': 1,
        'IMAGE': 3,
        'VOICE': 34,
        'PUSHMAIL': 35,
        'QQ_OFFLINE': 36,
        'FRIEND_RECOMMENDATION': 40,
        'EMOJI': 47,
        'SYSTEM': 10000
    }

    MSG_DEST = {
        'OUT': 0,
        'IN': 1
    }

    def __init__(self, db):
        self.__db = db

    def get_cids(self):
        master = self.__db.reflect(TBL_MASTER_NAME)
        stmt = select([master.c.name], and_(master.c.type == 'table',
            master.c.name.like(TBL_CHAT_PATTERN)))
        ret = []
        result = self.__db.conn.execute(stmt)
        for row in result:
            ret.append(row[0])
        result.close()
        return ret

    def get_info(self, cid):
        tbl = self.__db.reflect(cid)
        stmt = select([select([func.count(tbl.c.MesLocalID)]).as_scalar(),
            tbl.c.Message, tbl.c.CreateTime, tbl.c.Type, tbl.c.Des]).\
                order_by(tbl.c.CreateTime.desc()).limit(1)
        result = self.__db.conn.execute(stmt)
        row = result.fetchone()
        result.close()
        return {'count': row[0],
                'last_msg_content': row[1],
                'last_msg_ctime': row[2],
                'last_msg_type': row[3],
                'last_msg_dest': row[4]}

    def get_messages(self, cid):
        tbl = self.__db.reflect(cid)
        stmt = select([tbl.c.MesLocalID, tbl.c.CreateTime, tbl.c.Message,
            tbl.c.Type, tbl.c.Des])
        result = self.__db.conn.execute(stmt)
        for row in result:
            yield {'id': row[0],
                   'ctime': row[1],
                   'content': row[2],
                   'type': row[3],
                   'dest': row[4]}
        result.close()
