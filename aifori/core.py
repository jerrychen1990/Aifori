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
from typing import Iterable, List
from pydantic import BaseModel, Field
from aifori.config import AGENT_DIR, SESSION_DIR
from liteai.core import Message as LMessage
import uuid
from snippets import dump
from loguru import logger


class Message(LMessage):
    name: str = Field(description="user name")


class UserMessage(Message):
    role: str = "user"


class AssistantMessage(Message):
    role: str = "assistant"


class StreamMessage(Message):
    content: Iterable[str] = Field(description="stream content")


class StreamAssistantMessage(StreamMessage, AssistantMessage):
    pass


class AgentInfo(BaseModel):
    name: str = Field(description="assistant name")
    role: str = Field(description="assistant role")
    desc: str = Field(description="assistant description")


class Memory(BaseModel):
    def add_message(self, message: Message):
        raise NotImplementedError

    def to_llm_messages(self) -> List[Message]:
        raise NotImplementedError

    # def to_json(self) -> dict:
    #     raise NotImplementedError


class Voice(BaseModel):
    voice_file: str = Field(description="voice file path")
    content: bytes = Field(description="voice content")


class Agent:
    def __init__(self, name: str, desc: str, id: str = None):
        self.id = id if id else str(uuid.uuid4())
        self.name = name
        self.desc = desc

    @abstractmethod
    def chat(self, message: Message, stream=False, **kwargs) -> Message | StreamMessage:
        raise NotImplementedError

    @abstractmethod
    def speak(self, message: Message, stream=False, **kwargs) -> Voice:
        raise NotImplementedError

    @abstractmethod
    def remember(self, message):
        raise NotImplementedError

    def get_config(self):
        return dict(name=self.name, desc=self.desc, id=self.id)

    def save(self):
        agent_config_path = os.path.join(AGENT_DIR, f"{self.id}.json")
        config = self.get_config()
        logger.info(f"save agent {config} to {agent_config_path}")
        dump(config, agent_config_path)
        return agent_config_path


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
