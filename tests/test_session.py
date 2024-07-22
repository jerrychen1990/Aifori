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
AGENT_ID = "ut_agent"
logger = set_logger("dev", __name__)


class TestSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("start test session")
        cls.session_id = "ut_session"

    def test_message(self):
        SESSION_MANAGER.add_message(message=UserMessage(user_id=USER_ID, content="你好"),
                                    to_id=AGENT_ID, to_role="assistant", session_id=self.session_id)
        SESSION_MANAGER.add_message(message=AssistantMessage(user_id=AGENT_ID, content="你好呀，我叫Aifori"),
                                    to_id=USER_ID, to_role="user", session_id=self.session_id)
        messages = SESSION_MANAGER.get_history(related_ids=[USER_ID, AGENT_ID], limit=2)
        logger.info(f"{messages=}")
        self.assertEquals(2, len(messages))

        SESSION_MANAGER.clear_session(self.session_id)
        messages = SESSION_MANAGER.get_history(related_ids=[USER_ID, AGENT_ID], limit=2)
        logger.info(f"{messages=}")
        assert messages == []
