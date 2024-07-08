#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 17:14:50
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import copy
from typing import List
from aifori.core import Memory, Message, Memory
from liteai.core import Message


class RawMemory(Memory):
    def __init__(self, size: int = 10, history: List[Message | dict] = []):
        self.size = size
        self.history: List[Message] = [e if isinstance(e, Message) else Message(**e) for e in history]

    def to_llm_messages(self) -> List[Message]:
        return copy.copy(self.history)
