#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 17:47:34
@Author  :   ChenHao
@Description  :   api层
@Contact :   jerrychen1990@gmail.com
'''
from aifori.agent import AIAgent
from aifori.config import *
from aifori.core import Session
from snippets import load


def get_session(session_id: str) -> Session:
    file_path = os.path.join(SESSION_DIR, session_id+".json")
    session_config = load(file_path)
    session = Session.model_validate(session_config)
    return session


def get_assistant(assistant_id: str) -> AIAgent:
    config_path = os.path.join(AGENT_DIR, assistant_id+".json")
    assistant = AIAgent.from_config(config_path)
    return assistant
