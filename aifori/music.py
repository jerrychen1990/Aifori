#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/08/13 14:37:13
@Author  :   ChenHao
@Description  :   音乐相关
@Contact :   jerrychen1990@gmail.com
'''
import os
from loguru import logger
from aifori.config import DEFAULT_VOICE_CHUNK_SIZE, MUSIC_DIR
from liteai.core import Parameter, ToolDesc, Voice
from liteai.voice import file2voice, play_voice


def get_music_voice(desc: str) -> Voice:
    logger.debug(f"search music with : {desc=}")
    music_path = os.path.join(MUSIC_DIR, "the_moon_song_sample.mp3")
    logger.debug(f"play music : {music_path}")
    voice = file2voice(music_path)
    return voice


MusicToolDesc = ToolDesc(name="play_music", description="根据描述播放音乐",
                         parameters=[Parameter(name="music_desc", description="音乐描述", type="string", required=True)],
                         content_resp="正在播放音乐")


if __name__ == "__main__":
    voice = get_music_voice("dnll")
    play_voice(voice, buffer_size=DEFAULT_VOICE_CHUNK_SIZE)
