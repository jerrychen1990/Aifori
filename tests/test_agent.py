#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/04 15:14:54
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import unittest
from aifori.agent import *
from loguru import logger
from snippets import set_logger


class TestAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_logger("dev", __name__)
        logger.info("start test agent")

    def test_agent_chat(self):
        agent_info = AgentInfo(
            name="Emohaa", desc="Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话", role="assistant")
        memory = RawMemory(size=10, history=[])
        agent = AIAgent(agent_info=agent_info, memory=memory)
        message: AssistantMessage = UserMessage(content="你好，我最近心情不好，不知道该怎么办", name="Nobody")
        resp = agent.chat(message, max_tokens=64)
        logger.info(resp)

        message: AssistantMessage = UserMessage(content="能给我唱首歌么", name="Nobody")
        resp = agent.chat(message, max_tokens=64)
        print(resp)

        agent_path = agent.save()
        agent = AIAgent.load(agent_path)

        message: AssistantMessage = UserMessage(content="详细介绍刚才的歌", name="Nobody")
        resp = agent.chat(message, max_tokens=64)
        print(resp)
