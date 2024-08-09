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
from liteai.core import Voice
import uuid
from snippets import dump, load
from loguru import logger


class Message(LMessage):
    user_id: str = Field(description="agent的id")


class UserMessage(Message):
    role: str = "user"


class AgentMessage(Message):
    role: str = "assistant"


class StreamMessage(Message):
    content: Iterable[str] = Field(description="stream content")


class StreamAgentMessage(StreamMessage):
    role: str = "agent"


class AgentInfo(BaseModel):
    name: str = Field(description="agent name")
    role: str = Field(description="agent role")
    desc: str = Field(description="agent description")


class Memory(BaseModel):
    def add_message(self, message: Message):
        raise NotImplementedError

    def to_llm_messages(self) -> List[Message]:
        raise NotImplementedError

class BaseUser:
    role = "UNK"

    def __init__(self, name: str, desc: str, id: str = None, *args, **kwargs):
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
        return dict(name=self.name, desc=self.desc, id=self.id, role=self.role)

    @classmethod
    def get_config_path(cls, id: str):
        return os.path.join(AGENT_DIR, cls.role, f"{id}.json")

    def save(self):
        config_path = self.get_config_path(self.id)
        config = self.get_config()
        logger.info(f"save {self.role}'s {config} to {config_path}")
        dump(config, config_path)
        return config_path

    @classmethod
    def from_config(cls, id: str):
        config_path = cls.get_config_path(id)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"{cls.role}'s config for {id} not found!")
        data = load(config_path)
        logger.debug(f"load {cls.role} from {config_path}")
        return cls(**data)

    @classmethod
    def delete(cls, id: str):
        config_path = cls.get_config_path(id)
        if os.path.exists(config_path):
            logger.info(f"delete {cls.role} from {config_path}")
            os.remove(config_path)


class Session(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, description="session id")
    history: list[Message] = Field(default_factory=list, description="session history")
    agent_info: AgentInfo = Field(description="agent")
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
