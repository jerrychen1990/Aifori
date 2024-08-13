#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/19 15:32:20
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import os
from typing import List

from sqlalchemy import and_, desc, or_
from aifori.core import AssistantMessage, Message
from aifori.config import AIFORI_ENV, LOG_HOME, MEM_ON
from aifori.db import DB, MessageORM
from aifori.task import add_message2memory
from loguru import logger
from snippets import set_logger, jdumps


logger = set_logger(AIFORI_ENV, __name__,  std=False, log_dir=os.path.join(LOG_HOME, "session"))


class SessionManager:

    def add_message(self, message: Message, from_id: str, to_id: str, to_role: str, session_id: str):
        message_info = dict(content=message.content, from_id=from_id, to_id=to_id, from_role=message.role,
                            to_role=to_role, session_id=session_id)
        if isinstance(message, AssistantMessage):
            message_info["tool_calls"] = jdumps(message.tool_calls)
        orm_message = MessageORM(**message_info)

        DB.add(orm_message)
        DB.commit()
        DB.refresh(orm_message)
        logger.info(f"add message {jdumps(orm_message.to_dict(), indent=None)}")
        if MEM_ON:
            add_message2memory.delay(orm_message.to_dict())

    def get_history(self, _from: str | List[str] = None, to: str | List[str] = None, operator="and", session_id: str = None, limit=10) -> List[Message]:
        logger.debug(f"get history with {_from=}. {to=}, {session_id=}, {limit=}")
        query = DB.query(MessageORM)
        if session_id:
            query = query.filter(MessageORM.session_id == session_id)
        filter_phase = None
        if _from:
            _from = [_from] if isinstance(_from, str) else _from
            filter_phase = MessageORM.from_id.in_(_from)
        if to:
            to = [to] if isinstance(to, str) else to
            tmp_phase = MessageORM.to_id.in_(to)

            if filter_phase is not None:
                if operator == "and":
                    filter_phase = and_(filter_phase, tmp_phase)
                else:
                    filter_phase = or_(filter_phase, tmp_phase)
            else:
                filter_phase = MessageORM.to_id.in_(to)

        if filter_phase is not None:
            query = query.filter(filter_phase)

        orm_messages: List[MessageORM] = query.order_by(desc(MessageORM.id)).limit(limit).all()
        orm_json_messages = [m.to_dict() for m in orm_messages]
        logger.debug(f"get history with {orm_json_messages=}")

        messages = [m.to_message() for m in orm_messages[::-1]]
        return messages

    def clear_session(self, session_id: str):
        logger.info(f"clear session with {session_id=}")
        DB.query(MessageORM).filter(MessageORM.session_id == session_id).delete()
        DB.commit()


SESSION_MANAGER = SessionManager()
