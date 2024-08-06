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
import mem0


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
    agent_id: str = Field(description="The id of the agent")
    size: int = Field(default=10, description="The size of the memory")

    def to_llm_messages(self) -> List[Message]:
        return None


MEM = mem0.Memory()

# MEM = mem0.Memory.from_config(MEM_CONFIG)


# class Mem0Memory(Memory):
#     agent_id: str = Field(description="The id of the agent")
#     size: int = Field(default=10, description="The size of the memory")

#     def to_llm_messages(self) -> List[Message]:
#         messages = _MEM.get_all(agent_id=self.agent_id, limit=self.size)

#         logger.debug(f"{messages=}")
#         return messages

#     def add_message(self, message: Message, to_id: str) -> None:
#         user_id, agent_id = message.user_id, to_id
#         if message.role != "user":
#             user_id, agent_id = agent_id, user_id
#         logger.debug(f"add message {user_id=}, {agent_id=} {message.content=}")
#         rs = _MEM.add(message.content, user_id=user_id, agent_id=agent_id)
#         logger.info(rs)
