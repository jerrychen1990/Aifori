#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/02 17:07:28
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import copy
from loguru import logger
from aifori.config import *
from aifori.core import *
from aifori.memory import MEM, DBMemory
from liteai import api as liteai_api
from aifori.session import SESSION_MANAGER
from liteai.api import tts
from liteai.core import ToolDesc, Voice


class AIAgent(BaseUser):
    role = "assistant"

    def __init__(self, model: str, voice_config: dict = {}, tools: List[ToolDesc | dict] = [], **kwargs):
        super().__init__(**kwargs)
        self.memory = DBMemory(agent_id=self.id)
        self.model = model
        self.voice_config = voice_config
        self.system_template = DEFAULT_SYSTEM_TEMPLATE
        self.tools = [e if isinstance(e, ToolDesc) else ToolDesc(**e) for e in tools]

    def _build_system(self, user_id: str) -> str:
        user = Human.from_config(id=user_id)

        system = self.system_template.format(agent_name=self.name, agent_desc=self.desc, user_name=user.name, user_desc=user.desc)
        logger.debug(f"{system=}")
        return system

    def _static_response(self, resp: str, stream: bool, **kwargs) -> Message:
        if stream:
            return AssistantMessage(content=(e for e in resp), user_id=self.id)
        return AssistantMessage(content=resp, user_id=self.id)

    def _get_memory(self, message: UserMessage) -> str:
        mems = MEM.search(query=message.content, user_id=message.user_id)
        logger.debug(f"get {mems=}")
        mems = [f"{idx}. {mem['text']}" for idx, mem in enumerate(mems, start=1)]
        mems = "可供参考的历史记忆:\n" + "\n".join(mems)
        return mems

    def chat(self, user_id: str, message: UserMessage,  session_id=None, recall_memory=False, stream=False,  ** kwargs) -> AssistantMessage:
        user = Human.from_config(id=user_id)
        history = SESSION_MANAGER.get_history(_from=[self.id, user_id], to=[self.id, user_id], session_id=session_id)
        meta = dict(user_info=user.desc, user_name=user.name, bot_info=self.desc, bot_name=self.name)

        system = self._build_system(user_id=user_id)

        user_content = message.content
        if recall_memory:
            mem = self._get_memory(message=message)
            user_content = mem+"\n"+user_content
        message = dict(role="user", content=user_content)
        messages = [dict(role="system", content=system)] + history + [message]

        kwargs["handle_system"] = False

        llm_resp = liteai_api.chat(model=self.model, messages=messages, stream=stream, meta=meta,
                                   tools=self.tools, **kwargs, log_level="DEBUG")

        return AssistantMessage(content=llm_resp.content, tool_calls=llm_resp.tool_calls)

    def speak(self, message: Message | str, stream=True, voice_path: str = None, **kwargs) -> Voice:
        speak_config = copy.copy(self.voice_config)
        speak_config.update(**kwargs)

        if isinstance(message, Message):
            text = message.content
        else:
            text = message
        voice = tts(text=text, model="speech-01-turbo", stream=stream, tgt_path=voice_path, **kwargs, log_level=LITE_AI_LOG_LEVEL)
        return voice

    def get_config(self):
        config = super().get_config()
        config.update(model=self.model, tools=self.tools)
        return config


class Human(BaseUser):
    role = "user"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
