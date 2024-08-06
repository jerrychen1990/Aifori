#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/19 13:51:53
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import unittest
from aifori.agent import *
from loguru import logger
from snippets import set_logger

AGENT_ID = "ut_agent_id"
USER_ID = "ut_user_id"


@unittest.skip("skip test memory")
class TestMemory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_logger("dev", __name__)
        logger.info("start test memory")

    # def test_mem0(self):
    #     memory = Mem0Memory(agent_id=AGENT_ID)
    #     memory.add_message(message=UserMessage(user_id=USER_ID, content="你好，我叫Nobody"), to_id=AGENT_ID)
    #     memory.add_message(message=AssistantMessage(user_id=AGENT_ID, content="你好，我叫Aifori"), to_id=USER_ID)
    #     messages = memory.to_llm_messages()
    #     logger.info(messages)

    # def test_db_mem(self):
    #     memory = DBMemory(agent_id=AGENT_ID)
    #     memory.add_message(message=UserMessage(user_id=USER_ID, content="你好，我叫Nobody"), to_id=AGENT_ID)
    #     memory.add_message(message=AssistantMessage(user_id=AGENT_ID, content="你好，我叫Aifori"), to_id=USER_ID)
    #     messages = memory.to_llm_messages()
    #     logger.info(messages)
