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
from aifori.config import AGENT_DIR, SESSION_DIR
from liteai.core import Message as LMessage
import uuid
from snippets import dump, load
from loguru import logger


class Message(LMessage):
    name: str = Field(description="user name")


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


class Memory(BaseModel):
    def add_message(self, message: Message):
        raise NotImplementedError

    def to_llm_messages(self) -> List[Message]:
        raise NotImplementedError

    def to_json(self) -> dict:
        raise NotImplementedError


class Agent:
    def __init__(self, agent_info: AgentInfo, memory: Memory):
        self.name = agent_info.name
        self.desc = agent_info.desc
        self.role = agent_info.role
        self.agent_info = agent_info
        self.memory = memory

    def _chat(self, message: Message, stream=False) -> Message:
        raise NotImplementedError

    @abstractmethod
    def chat(self, message: Message, stream=False, do_remember=True, **kwargs) -> Message:
        resp_message = self._chat(message, stream, **kwargs)
        if do_remember:
            self.remember(message)
            self.remember(resp_message)
        return resp_message

    @abstractmethod
    def remember(self, message: Message):
        raise NotImplementedError

    def save(self):
        agent_config_path = os.path.join(AGENT_DIR, f"{self.name}.json")
        data = dict(agent_info=self.agent_info.model_dump(), memory=self.memory.to_json())
        logger.info(f"save agent {data} to {agent_config_path}")
        dump(data, agent_config_path)
        return agent_config_path

    @classmethod
    def load(cls, path: str):
        data = load(path)
        agent_info = AgentInfo(**data["agent_info"])
        memory = Memory(**data["memory"])
        return cls(agent_info=agent_info, memory=memory)


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
