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
from aifori.api import get_assistant
from loguru import logger
from aifori.client import AiForiClient
from aifori.tts import play_voice
from snippets import set_logger


class TestAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_logger("dev", __name__)
        logger.info("start test agent")
        cls.agent_id = "ut_agent"
        cls.user_id = "ut_user"

    def test_agent_chat(self):
        memory = RawMemory(size=10, history=[])
        name = "Emohaa"
        desc = "Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话"
        agent = AIAgent(id=self.agent_id, name=name, desc=desc, memory=memory, model="GLM-4-Flash")

        # 测试问答
        message: AssistantMessage = UserMessage(content="你好，我最近心情不好，不知道该怎么办", id=self.user_id)
        resp = agent.chat(message, max_tokens=128)
        logger.info(resp)

        # 测试流式
        message: AssistantMessage = UserMessage(content="能给我推荐三首歌么", id=self.user_id)
        resp = agent.chat(message, max_tokens=128, stream=True, do_remember=True)
        logger.info(f"{resp=}")
        for item in resp.content:
            logger.info(item)

        # 测试save/load
        agent.save()
        agent = get_assistant(agent.id)

        # 测试多轮
        message: AssistantMessage = UserMessage(content="详细介绍一下第三首", id=self.user_id)
        resp = agent.chat(message, max_tokens=64)
        logger.info(resp)

    def test_speak(self):
        agent = get_assistant(self.agent_id)
        message = AssistantMessage(content="你好，我叫Aifori, 有什么能帮到你的么？", id=self.agent_id)
        voice = agent.speak(message)
        logger.info(f"{voice.content=}")
        play_voice(voice.content)
