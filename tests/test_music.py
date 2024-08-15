#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/08/15 10:13:04
@Author  :   ChenHao
@Description  :   测试music
@Contact :   jerrychen1990@gmail.com
'''
import unittest

from aifori.api import *
# from aifori.client import handle_chat_stream
from aifori.music import get_music_voice
from liteai.voice import play_voice
from snippets.logs import set_logger


class TestMusic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_logger("dev", __name__)
        logger.info("start test assistant")
        cls.assistant_id = "ut_assistant"
        cls.user_id = "ut_user"
        cls.session_id = "ut_session"

    def test_play_music(self):
        voice: Voice = get_music_voice("dnll")
        play_voice(voice)
