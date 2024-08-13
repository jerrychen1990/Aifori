#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/18 17:23:23
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import unittest
from aifori.agent import *
from snippets import set_logger
from aifori.session import SESSION_MANAGER


USER_ID = "ut_user"
ASSISTANT_ID = "ut_agent"
logger = set_logger("dev", __name__)


class TestSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("start test session")
        cls.session_id = "ut_session"

    def test_message(self):
        SESSION_MANAGER.clear_session(self.session_id)

        SESSION_MANAGER.add_message(message=UserMessage(content="你好"),
                                    from_id=USER_ID,
                                    to_id=ASSISTANT_ID, to_role="agent", session_id=self.session_id)
        SESSION_MANAGER.add_message(message=AssistantMessage(content="你好呀，我叫Aifori"), from_id=ASSISTANT_ID,
                                    to_id=USER_ID, to_role="user", session_id=self.session_id)
        SESSION_MANAGER.add_message(message=UserMessage(content="1+1=2吗"), from_id=USER_ID,
                                    to_id=ASSISTANT_ID, to_role="agent", session_id=self.session_id)
        SESSION_MANAGER.add_message(message=AssistantMessage(content="是的，1+1=2"), from_id=ASSISTANT_ID,
                                    to_id=USER_ID, to_role="user", session_id=self.session_id)

        messages = SESSION_MANAGER.get_history(_from=[USER_ID, ASSISTANT_ID], to=[USER_ID, ASSISTANT_ID], limit=10)
        logger.info(f"{messages=}")
        self.assertEquals(4, len(messages))
        messages = SESSION_MANAGER.get_history(_from=ASSISTANT_ID, limit=10)
        logger.info(f"{messages=}")
        self.assertEquals(2, len(messages))

        messages = SESSION_MANAGER.get_history(_from=ASSISTANT_ID, to=ASSISTANT_ID, operator="or", limit=10)
        logger.info(f"{messages=}")
        self.assertEquals(4, len(messages))

        SESSION_MANAGER.clear_session(self.session_id)

        messages = SESSION_MANAGER.get_history(_from=ASSISTANT_ID, limit=10)
        logger.info(f"{messages=}")
        self.assertEquals(0, len(messages))
