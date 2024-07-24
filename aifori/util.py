#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/24 18:23:19
@Author  :   ChenHao
@Description  :  工具模块
@Contact :   jerrychen1990@gmail.com
'''
from loguru import logger


def show_stream_content(stream_content):
    full_content = ""
    tmp_chunk = ""
    for chunk in stream_content:
        tmp_chunk += chunk
        if len(tmp_chunk) > 10:
            logger.info(f"{tmp_chunk=}")
            full_content += tmp_chunk
            tmp_chunk = ""
    full_content += tmp_chunk
    logger.info(f"{full_content=}")
    return full_content
