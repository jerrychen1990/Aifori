#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/24 18:23:19
@Author  :   ChenHao
@Description  :  工具模块
@Contact :   jerrychen1990@gmail.com
'''
from loguru import logger

from aifori.core import Message


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
    logger.info(f"message from {message.role}, {message.user_id}")
    if isinstance(message.content, str):
        logger.info(f"{message.content=}")
        return message.content
    else:
        return show_stream_content(message.content)
        
    
