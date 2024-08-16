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
from aifori.api import create_assistant, create_user, get_assistant, clear_session
from loguru import logger
from aifori.config import *
from aifori.music import MusicToolDesc
from aifori.util import show_message
from snippets import set_logger
from liteai.core import Voice
from liteai.voice import play_voice


class TestAssistant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_logger("dev", __name__)
        logger.info("start test assistant")
        cls.assistant_id = "ut_assistant"
        cls.user_id = "ut_user"
        cls.assistant = create_assistant(id=cls.assistant_id, name=DEFAULT_AI_NAME, desc=DEFAULT_AI_DESC, model=DEFAULT_MODEL, exists_ok=True)
        cls.user = create_user(id=cls.user_id, name=DEFAULT_USER_NAME, desc=DEFAULT_USER_DESC, exists_ok=True)

    def test_assistant_chat(self):
        session_id = "ut_session"

        # 测试问答
        message: UserMessage = UserMessage(content="你好，我最近心情不好，不知道该怎么办", user_id=self.user_id, session_id=session_id)
        resp = self.assistant.chat(self.user_id, message, max_tokens=128)
        show_message(resp)

        # 测试流式
        message: UserMessage = UserMessage(content="能给我推荐三首歌么", user_id=self.user_id, session_id=session_id)
        resp = self.assistant.chat(self.user_id, message, max_tokens=128, stream=True, do_remember=True)
        show_message(resp)

        # 测试多轮
        message: UserMessage = UserMessage(content="详细介绍一下第三首", user_id=self.user_id, session_id=session_id)
        resp = self.assistant.chat(self.user_id, message, max_tokens=64)
        show_message(resp)
        # 清空session
        clear_session(session_id)

    def test_speak(self):
        assistant = get_assistant(self.assistant_id)
        message = AssistantMessage(content="你好，我叫Aifori, 有什么能帮到你的么？", user_id=self.assistant_id)
        voice: Voice = assistant.speak(message)
        play_voice(voice=voice)

    def test_recommend_music(self):
        tools = [MusicToolDesc]
        assistant = create_assistant(id="ut_tool_assistant", name="ut_tool_assistant",
                                     desc="ut_tool_assistant", model=DEFAULT_MODEL, exists_ok=True, tools=tools)

        resp = assistant.chat(self.user_id, UserMessage(content="推荐一首欢快的歌曲", user_id=self.user_id))
        logger.info(resp)
        show_message(resp)
