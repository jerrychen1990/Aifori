#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/08/09 11:09:54
@Author  :   ChenHao
@Description  :   测试aifori的api函数
@Contact :   jerrychen1990@gmail.com
'''


import unittest

from aifori.api import *
from aifori.client import decode_chunks
from aifori.core import ChatRequest
# from aifori.client import handle_chat_stream
from aifori.music import MusicToolDesc
from aifori.util import show_message
from liteai.core import LLMGenConfig
from liteai.voice import play_file, play_voice
from snippets.logs import set_logger


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_logger("dev", __name__)
        logger.info("start test assistant")
        cls.assistant_id = "ut_assistant"
        cls.user_id = "ut_user"
        cls.session_id = "ut_session"

    def test_assistant1(self):
        # Test creating a new assistant
        assistant = create_assistant(name=self.assistant_id, desc=self.assistant_id, id=self.assistant_id, model=DEFAULT_MODEL, do_save=True)
        self.assertIsNotNone(assistant)

    def test_create_user2(self):
        # Test creating a new user
        user = create_user(name=self.user_id, desc=self.user_id, id=self.user_id, do_save=True)
        self.assertIsNotNone(user)

    def test_chat_assistant3(self):
        create_assistant(name=self.assistant_id, desc=self.assistant_id, id=self.assistant_id, model=DEFAULT_MODEL, do_save=True)
        create_user(name=self.user_id, desc=self.user_id, id=self.user_id, do_save=True)

        req = ChatRequest(assistant_id=self.assistant_id, user_id=self.user_id, session_id=self.session_id,
                          message="你好，你叫什么名字", do_remember=True)
        message = chat_assistant(req, stream=False)
        show_message(message)
        assert "ut_assistant" in message.content.lower()
        req = ChatRequest(assistant_id=self.assistant_id, user_id=self.user_id, session_id=self.session_id,
                          message="作一首古诗", do_remember=True)
        message = chat_assistant(req, stream=True)
        show_message(message)

    def test_speak_assistant(self):
        create_assistant(name=self.assistant_id, desc=self.assistant_id, id=self.assistant_id, model=DEFAULT_MODEL, do_save=True)
        voice_path = "./tmp/ut_test_api_speak.mp3"

        req = SpeakRequest(assistant_id=self.assistant_id, message="你好，我叫Aifori，有什么可以帮你的么", voice_path=voice_path)
        voice: Voice = speak_assistant(req, stream=True)
        logger.info(f"{voice.file_path=}")
        play_voice(voice)
        assert os.path.exists(voice.file_path)
        play_file(voice.file_path)

        voice_path = "./tmp/ut_test_api_speak_reply.mp3"

        req = SpeakRequest(assistant_id=self.assistant_id, message="你好，我是Nobody",
                           voice_config=dict(voice_id="junlang_nanyou", speed=.6, pitch=-4), voice_path=voice_path)
        voice: Voice = speak_assistant(req, stream=False)
        logger.info(f"{voice.file_path=}")
        assert os.path.exists(voice.file_path)
        play_voice(voice)

    def test_chat_music(self):

        tools = [MusicToolDesc]

        assistant = create_assistant(id="ut_tool_assistant", name="ut_tool_assistant",
                                     desc="ut_tool_assistant", model=DEFAULT_MODEL, exists_ok=True, tools=tools)
        create_user(name=self.user_id, desc=self.user_id, id=self.user_id, do_save=True)

        req = ChatRequest(assistant_id=assistant.id, user_id=self.user_id, session_id=self.session_id,
                          message="推荐一首欢快的歌曲", do_remember=True)
        message = chat_assistant(req, stream=False)
        

        show_message(message)

    def test_chat_speak_assistant(self):
        create_assistant(name=self.assistant_id, desc=self.assistant_id, id=self.assistant_id, model=DEFAULT_MODEL, do_save=True)
        create_user(name=self.user_id, desc=self.user_id, id=self.user_id, do_save=True)

        clear_session(self.session_id)

        return_voice = False
        req = ChatSpeakRequest(assistant_id=self.assistant_id, user_id=self.user_id, session_id=self.session_id,
                               message="你好，你叫什么名字", stream=True, do_remember=False, return_text=True, return_voice=return_voice)
        resp = chat_speak_assistant(req)
        message, voice = decode_chunks(resp, req.assistant_id, return_voice, local_file_path=None)
        message_content = show_message(message)
        assert "ut_assistant" in message_content.lower()
        assert voice is None

        return_voice = True
        server_voice_path = "./tmp/ut_test_api_chat_speak_server.mp3"
        local_voice_path = "./tmp/ut_test_api_chat_speak_local.mp3"
        req = ChatSpeakRequest(assistant_id=self.assistant_id, user_id=self.user_id, session_id=self.session_id,
                               message="作一首五言绝句", stream=True, do_remember=False, return_text=True, return_voice=return_voice,
                               voice_path=server_voice_path, llm_gen_config=LLMGenConfig(max_tokens=16))

        resp = chat_speak_assistant(req)
        message, voice = decode_chunks(resp, req.assistant_id, return_voice, local_voice_path)

        play_voice(voice)
        assert os.path.exists(voice.file_path)
        play_file(voice.file_path)

        assert os.path.exists(server_voice_path)
        play_file(server_voice_path)

    def test_rule_chat(self):
        # 测试规则问答
        create_assistant(name=self.assistant_id, desc=self.assistant_id, id=self.assistant_id, model=DEFAULT_MODEL, do_save=True)
        create_user(name=self.user_id, desc=self.user_id, id=self.user_id, do_save=True)

        req = ChatRequest(assistant_id=self.assistant_id, user_id=self.user_id, session_id=self.session_id,
                          message="我叫神尼名字", do_remember=False)
        message = chat_assistant(req, stream=True)

        message = show_message(message)
        self.assertEquals("你叫Nobody", message)

    def test_clear10(self):
        delete_assistant(id=self.assistant_id)
        with self.assertRaises(FileNotFoundError) as context:
            get_assistant(id=self.assistant_id)

        delete_user(id=self.user_id)
        with self.assertRaises(FileNotFoundError) as context:
            get_user(id=self.user_id)
