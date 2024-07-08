#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 17:47:34
@Author  :   ChenHao
@Description  :   api层
@Contact :   jerrychen1990@gmail.com
'''
from aifori.config import *
from aifori.core import Session
from snippets import load

def get_session(session_id):
    file_path = os.path.join(SESSION_DIR, session_id+".json") 
    session_config = load(file_path)   
    Session = Session(session_config)

    pass
