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
from aifori.api import create_agent, create_user, get_agent, clear_session
from loguru import logger
from aifori.config import *
from snippets import set_logger
from liteai.core import Voice
from liteai.voice import play_voice


class TestAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_logger("dev", __name__)
        logger.info("start test agent")
        cls.agent_id = "ut_agent"
        cls.user_id = "ut_user"
        cls.agent = create_agent(id=cls.agent_id, name=DEFAULT_AI_NAME, desc=DEFAULT_AI_DESC, model=DEFAULT_MODEL, exists_ok=True)
        cls.user = create_user(id=cls.user_id, name=DEFAULT_USER_NAME, desc=DEFAULT_USER_DESC, exists_ok=True)

    def test_rule_chat(self):
        # 测试规则问答
        message: AgentMessage = UserMessage(content="你好呀,你叫什么名字", user_id=self.user_id)
        resp = self.agent.chat(message, max_tokens=64)
        logger.info(resp)
        assert resp.content == "你好呀，我叫Aifori，很高兴认识你！"

    def test_agent_chat(self):
        session_id = "ut_session"
        

        # 测试问答
        message: UserMessage = UserMessage(content="你好，我最近心情不好，不知道该怎么办", user_id=self.user_id, session_id=session_id)
        resp = self.agent.chat(message, max_tokens=128)
        logger.info(resp)

        # 测试流式
        message: UserMessage = UserMessage(content="能给我推荐三首歌么", user_id=self.user_id, session_id=session_id)
        resp = self.agent.chat(message, max_tokens=128, stream=True, do_remember=True)
        logger.info(f"{resp=}")
        for item in resp.content:
            logger.info(item)

        # 测试多轮
        message: UserMessage = UserMessage(content="详细介绍一下第三首", user_id=self.user_id, session_id=session_id)
        resp = self.agent.chat(message, max_tokens=64)
        logger.info(resp)
        
        # 清空session
        clear_session(session_id)

    def test_lingxin_agent(self):
        lingxin_agent = create_agent(id="lingxin_agent", name="lingxin_agent", desc=DEFAULT_AI_DESC, model="emohaa", exists_ok=True)
        message = UserMessage(content="你好，我叫Aifori, 有什么能帮到你的么？", user_id=self.user_id)
        resp = lingxin_agent.chat(message, max_tokens=64)
        logger.info(resp)

    def test_speak(self):
        agent = get_agent(self.agent_id)
        message = AgentMessage(content="你好，我叫Aifori, 有什么能帮到你的么？", user_id=self.agent_id)
        voice: Voice = agent.speak(message)
        play_voice(voice=voice)
