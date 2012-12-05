# -*- coding: utf-8 -*-

"""
wechat.conversation
-------------------

This module defines ``Conversation`` which provides accesses to wechat
conversations data.
"""

from sqlalchemy.sql import select, and_, func

TBL_MASTER = 'sqlite_master'
TBL_CHAT_PATTERN = 'Chat_%'

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
        self._db = db
        self._tbl_master = self._db.reflect(TBL_MASTER)
        self._chat_tbls = {}

    def get_conversations(self):
        master = self._tbl_master
        stmt = select([master.c.name], and_(master.c.type == 'table',
            master.c.name.like(TBL_CHAT_PATTERN)))
        for row in self._db.conn.execute(stmt):
            cid = row[0]
            tbl = self._get_chat_tbl(cid)
            stmt = select([select([func.count(tbl.c.MesLocalID)]).as_scalar(),
                tbl.c.Message, tbl.c.CreateTime, tbl.c.Type, tbl.c.Des]).\
                    order_by(tbl.c.CreateTime.desc()).limit(1)
            result = self._db.conn.execute(stmt).fetchone()
            yield {'cid': cid,
                   'msg_count': result[0],
                   'last_msg_content': result[1],
                   'last_msg_ctime': result[2],
                   'last_msg_type': result[3],
                   'last_msg_dest': result[4]}

    def get_messages(self, cid):
        tbl = self._get_chat_tbl(cid)
        stmt = select([tbl.c.MesLocalID, tbl.c.CreateTime, tbl.c.Message,
            tbl.c.Type, tbl.c.Des])
        for row in self._db.conn.execute(stmt):
            yield {'id': row[0],
                   'ctime': row[1],
                   'content': row[2],
                   'type': row[3],
                   'dest': row[4]}

    def _get_chat_tbl(self, cid):
        if cid not in self._chat_tbls:
            self._chat_tbls[cid] = self._db.reflect(cid)
        return self._chat_tbls[cid]
