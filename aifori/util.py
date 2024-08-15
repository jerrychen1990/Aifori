#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/24 18:23:19
@Author  :   ChenHao
@Description  :  工具模块
@Contact :   jerrychen1990@gmail.com
'''
from loguru import logger

from aifori.config import DEFAULT_VOICE_CHUNK_SIZE
from aifori.core import Message
from liteai.core import Voice


def show_stream_content(stream_content, batch_size: int = 10):
    full_content = ""
    tmp_chunk = ""
    for chunk in stream_content:
        tmp_chunk += chunk
        if len(tmp_chunk) > batch_size:
            logger.info(f"chunk={tmp_chunk}")
            full_content += tmp_chunk
            tmp_chunk = ""
    full_content += tmp_chunk
    logger.info(f"{full_content=}")
    return full_content


def show_message(message: Message):
    logger.info(f"message from {message.role}:")
    if isinstance(message.content, str):
        logger.info(message.content)
        return message.content
    else:
        return show_stream_content(message.content)


def voice2api_stream(voice: Voice, chunk_size=DEFAULT_VOICE_CHUNK_SIZE):
    acc = b""
    for chunk in voice.byte_stream:
        acc += chunk
        while len(acc) > chunk_size:
            yield dict(voice_chunk=acc[:chunk_size])
            acc = acc[chunk_size:]
    if len(acc) > 0:
        yield dict(voice_chunk=acc)
