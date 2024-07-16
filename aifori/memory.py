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
from pydantic import Field


class RawMemory(Memory):
    size: int = Field(default=10, description="The size of the memory")
    history: List[Message] = Field(default=[], description="The history of the memory")

    def to_llm_messages(self) -> List[Message]:
        return copy.copy(self.history)

    def add_message(self, message: Message) -> None:
        self.history.append(message)

    # def to_json(self) -> dict:
    #     logger.debug(f"history: {self.history}")
    #     return {"size": self.size, "history": self.history}



class DBMemory(Memory):
    agent_id:str  = Field(default="", description="The id of the agent")

    def to_llm_messages(self) -> List[Message]:
        
        return copy.copy(self.history)

    def add_message(self, message: Message) -> None:
        self.history.append(message)
    