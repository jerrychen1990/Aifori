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


set_logger("DEV", __name__, "./logs")
load_dotenv()


# for k, v in st.secrets.items():
#     logger.info(f"set env {k}={v}")
#     os.environ[k] = v
