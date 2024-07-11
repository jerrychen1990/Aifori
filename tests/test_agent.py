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
        memory = RawMemory(size=10, history=[])
        name = "Emohaa"
        desc = "Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话"
        agent = AIAgent(id="test_agent", name=name, desc=desc, memory=memory, model="GLM-4-Flash")

        # 测试问答
        message: AssistantMessage = UserMessage(content="你好，我最近心情不好，不知道该怎么办", name="Nobody")
        resp = agent.chat(message, max_tokens=128)
        logger.info(resp)

        # 测试流式
        message: AssistantMessage = UserMessage(content="能给我推荐三首歌么", name="Nobody")
        resp = agent.chat(message, max_tokens=128, stream=True, do_remember=True)
        logger.info(f"{resp=}")
        for item in resp.content:
            logger.info(item)

        # 测试save/load
        agent_path = agent.save()
        agent = AIAgent.from_config(agent_path)

        # 测试多轮
        message: AssistantMessage = UserMessage(content="详细介绍一下第三首", name="Nobody")
        resp = agent.chat(message, max_tokens=64)
        logger.info(resp)
