#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/04 14:25:18
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import os
from snippets import set_logger
from dotenv import load_dotenv
from aifori.config import AIFORI_ENV, LOG_HOME


set_logger(AIFORI_ENV, __name__, log_dir=os.path.join(LOG_HOME, "aifori"), show_process=True)
load_dotenv()
