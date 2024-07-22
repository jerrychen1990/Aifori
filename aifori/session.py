#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/19 15:32:20
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

from typing import List

from sqlalchemy import and_, desc
from aifori.core import Message
from aifori.db import DB, MessageORM


from loguru import logger


class SessionManager:
    def add_message(self, message: Message, to_id: str, to_role: str, session_id: str):
        orm_message = MessageORM(content=message.content, from_id=message.user_id, to_id=to_id, from_role=message.role,
                                 to_role=to_role, session_id=session_id)

        logger.debug(f"add {orm_message=}")
        DB.add(orm_message)
        DB.commit()
        DB.refresh(orm_message)

    def get_history(self, related_ids: List[str] = None, session_id: str = None, limit=10) -> List[Message]:
        logger.debug(f"get history with {related_ids=}, {limit=}")

        query = DB.query(MessageORM)
        if session_id:
            query = query.filter(MessageORM.session_id == session_id)
        if related_ids:
            query = query.filter(and_(MessageORM.from_id.in_(related_ids), MessageORM.to_id.in_(related_ids)))

        orm_messages: List[MessageORM] = query.order_by(desc(MessageORM.id)).limit(limit).all()
        orm_json_messages = [m.to_dict() for m in orm_messages]
        logger.debug(f"get history with {orm_json_messages=}")

        messages = [m.to_message() for m in orm_messages[::-1]]
        return messages

    def clear_session(self, session_id: str):
        logger.debug(f"clear session with {session_id=}")
        DB.query(MessageORM).filter(MessageORM.session_id == session_id).delete()
        DB.commit()
        # DB.refresh(MessageORM)


SESSION_MANAGER = SessionManager()
