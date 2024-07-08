#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/04 14:25:18
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import os
import streamlit as st
from snippets import set_logger
from loguru import logger

set_logger("DEV", __name__, "./logs")


for k, v in st.secrets.items():
    logger.info(f"set env {k}={v}")
    os.environ[k] = v
