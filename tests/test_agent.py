#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/04 15:14:54
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import unittest
from her.agent import *


class TestAgent(unittest.TestCase):
    def test_agent(self):
        user_info = AgentInfo(name="user", desc="user")
        agent_info = AgentInfo(name="agent", desc="assistant")
        model = "glm-4-airx"
        messages = [dict(role="user", content="你好")]

        resp = chat_llm(user_info, agent_info, model=model, messages=messages, stream=True)
        for r in resp:
            print(r)
