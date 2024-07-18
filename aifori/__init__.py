#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/04 14:25:18
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


from snippets import set_logger
from dotenv import load_dotenv
from aifori.config import LOG_HOME


set_logger("DEV", __name__, LOG_HOME)
load_dotenv()
