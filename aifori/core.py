#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 16:53:50
@Author  :   ChenHao
@Description  :   core classes
@Contact :   jerrychen1990@gmail.com
'''


import os
from typing import List, Optional
from pydantic import BaseModel, Field
from aifori.config import AGENT_DIR, DEFAULT_TEXT_CHUNK_SIZE, DEFAULT_TTS_TEXT_CHUNK_SIZE, DEFAULT_VOICE_CHUNK_SIZE, DEFAULT_VOICE_CONFIG
from liteai.core import LLMGenConfig, Message, ToolCall
import uuid
from snippets import dump, load
from loguru import logger


class UserMessage(Message):
    role: str = "user"


class AssistantMessage(Message):
    role: str = "assistant"
    tool_calls: Optional[List[ToolCall]] = Field(default=[], description="tool calls")

    @property
    def is_stream(self):
        return not isinstance(self.content, str)


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
        else:
            logger.warning(f"{cls.role} config file: {config_path} not exists, will not delete")


class ChatRequest(BaseModel):
    assistant_id: str = Field(description="AIAgent的ID,唯一键", examples=["test_assistant"])
    user_id: str = Field(description="用户的ID,唯一键", examples=["test_user"])
    session_id: str = Field(default=None, description="对话的ID,唯一键", examples=["test_session"])
    message: str = Field(description="用户发送的消息", examples=["你好呀，你叫什么名字？"])
    do_remember: bool = Field(default=False, description="Agent是否记忆这轮对话")
    recall_memory: bool = Field(default=False, description="是否唤起长期记忆")
    llm_gen_config: LLMGenConfig = Field(default=LLMGenConfig(), description="llm的配置")


class SpeakRequest(BaseModel):
    assistant_id: str = Field(description="AIAgent的ID,唯一键", examples=["test_assistant"])
    message: str = Field(description="用户发送的消息", examples=["你好呀，你叫什么名字？"])
    voice_path: Optional[str] = Field(default=None, description="音频文件存储路径", examples=[None])
    voice_config: dict = Field(default=DEFAULT_VOICE_CONFIG, description="tts的配置")
    voice_chunk_size: int = Field(default=DEFAULT_VOICE_CHUNK_SIZE, description="默认音频字节chunk(byte)大小, mp3格式")


class ChatSpeakRequest(ChatRequest):
    return_text: bool = Field(default=True, description="是否返回文字")
    text_chunk_size: int = Field(default=DEFAULT_TEXT_CHUNK_SIZE, description="返回的文字chunk(字符)的token大小")
    voice_config: dict = Field(default=DEFAULT_VOICE_CONFIG, description="tts的配置")
    return_voice: bool = Field(default=False, description="是否返回音频")
    tts_text_chunk_size: int = Field(default=DEFAULT_TTS_TEXT_CHUNK_SIZE, description="积累多少个字符请求一次tts")
    voice_chunk_size: int = Field(default=DEFAULT_VOICE_CHUNK_SIZE, description="默认音频字节chunk(byte)大小, mp3格式")
    voice_path: Optional[str] = Field(default=None, description="音频文件存储路径", examples=[None])
