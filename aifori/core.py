#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 16:53:50
@Author  :   ChenHao
@Description  :   core classes
@Contact :   jerrychen1990@gmail.com
'''


from abc import abstractmethod
from typing import List
from pydantic import BaseModel, Field
from liteai.core import Message
import uuid


class HumanMessage(Message):
    role: str = "user"

    # class Config:
    #     arbitrary_types_allowed = True


class AssistantMessage(Message):
    role: str = "assistant"

    # class Config:
    #     arbitrary_types_allowed = True


class AgentInfo(BaseModel):
    name: str = Field(description="assistant name")
    role: str = Field(description="assistant role")
    desc: str = Field(description="assistant description")


class Memory:
    def add(self, message: Message):
        raise NotImplementedError

    def to_llm_messages(self) -> List[Message]:
        raise NotImplementedError


class Agent:
    def __init__(self, agent_info: AgentInfo, memory: Memory):
        self.name = agent_info.name
        self.desc = agent_info.desc
        self.role = agent_info.role
        self.memory = memory

    @abstractmethod
    def chat(self, name: str, message: Message, stream=False) -> Message:
        raise NotImplementedError


class Session(BaseModel):
    id: str = Field(default=uuid.uuid4, description="session id")
    history: list[Message] = Field(default_factory=list, description="session history")
    assistant: Agent = Field(description="assistant")
    human: Agent = Field(description="human ")

    class Config:
        arbitrary_types_allowed = True
        
    
