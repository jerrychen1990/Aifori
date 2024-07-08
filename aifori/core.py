#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 16:53:50
@Author  :   ChenHao
@Description  :   core classes
@Contact :   jerrychen1990@gmail.com
'''


from abc import abstractmethod
import os
from typing import List
from pydantic import BaseModel, Field
from aifori.config import SESSION_DIR
from liteai.core import Message
import uuid
from snippets import dump
from loguru import logger


class UserMessage(Message):
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
    id: str = Field(default_factory=uuid.uuid4, description="session id")
    history: list[Message] = Field(default_factory=list, description="session history")
    assistant_info: AgentInfo = Field(description="assistant")
    user_info: AgentInfo = Field(description="human ")

    class Config:
        arbitrary_types_allowed = True

    def to_json(self):
        rs = self.model_dump(exclude={"history"})
        rs.update(history_len=len(self.history))
        return rs

    def save(self):
        tgt_path = os.path.join(SESSION_DIR, f"{self.id}.json")
        logger.info(f"save session to {tgt_path}")

        dump(self.model_dump(), tgt_path)
