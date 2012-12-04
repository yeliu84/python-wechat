# -*- coding: utf-8 -*-

"""
wechat.friend
-------------

This module defines ``Friend`` which provides accesses to wechat friends data.
"""

import re

from sqlalchemy.sql import select, and_, not_

TBL_FRIEND = 'Friend'
TBL_FRIEND_EXT = 'Friend_Ext'

RE_REMARK = re.compile(r'''<1>(?P<remark>.+)</1>''')
RE_AVATAR_URL = re.compile(
    r'''<HeadImgUrl>(?P<avatar>.+)</HeadImgUrl>
        <HeadImgHDUrl>(?P<avatar_hd>.+)</HeadImgHDUrl>''', re.VERBOSE)

class Friend:
    FRIEND_GENDERS = {
        'UNKNOWN': 0,
        'MALE': 1,
        'FEMALE': 2
    }

    FRIEND_TYPES = {
        'SELF': 4
    }

    def __init__(self, db):
        self.__db = db
        self.__tbl_friend = db.reflect(TBL_FRIEND)
        self.__tbl_friend_ext = db.reflect(TBL_FRIEND_EXT)

    def get_friends(self):
        friend = self.__tbl_friend
        stmt = select([friend.c.UsrName, friend.c.NickName, friend.c.Sex,
            friend.c.ShortPY, friend.c.Img, friend.c.Type,
            friend.c.LastChatTime],
                and_(friend.c.Type > 0,
                    not_(friend.c.UsrName.like('%@t.qq.com')),
                    not_(friend.c.UsrName.like('%@chatroom'))))
        for row in self.__db.conn.execute(stmt):
            ret = {'username': row[0],
                   'nickname': row[1],
                   'gender': row[2],
                   'remark': None,
                   'has_avatar': True if row[4] != 'IMG_NO' else False,
                   'type': row[5],
                   'last_chat_time': row[6]}
            m = RE_REMARK.match(row[3])
            if m:
                ret['remark'] = m.group('remark')
            yield ret

    def get_avatar(self, username):
        extra = self.__tbl_friend_ext
        stmt = select([extra.c.ConStrRes2], extra.c.UsrName == username)
        row = self.__db.conn.execute(stmt).fetchone()
        m = RE_AVATAR_URL.search(row[0])
        if m:
            return (m.group('avatar'), m.group('avatar_hd'))
        return None
