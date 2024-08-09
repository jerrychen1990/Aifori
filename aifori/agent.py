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
from aifori.config import DEFAULT_SYSTEM_TEMPLATE, LITE_AI_LOG_LEVEL
from aifori.core import BaseUser, AgentInfo, AgentMessage, Message, StreamAgentMessage, StreamMessage, UserMessage, Voice
from aifori.memory import MEM, DBMemory, RawMemory
from liteai import api as liteai_api
from aifori.rule import rule_match
from aifori.session import SESSION_MANAGER
from liteai.api import tts


class AIAgent(BaseUser):
    role = "agent"

    def __init__(self, model: str, voice_config: dict = {}, **kwargs):
        super().__init__(**kwargs)
        self.memory = DBMemory(agent_id=self.id)
        self.model = model
        self.voice_config = voice_config
        self.system_template = DEFAULT_SYSTEM_TEMPLATE

    def _build_system(self, user_id: str) -> str:
        user = Human.from_config(id=user_id)

        system = self.system_template.format(agent_name=self.name, agent_desc=self.desc, user_name=user.name, user_desc=user.desc)
        logger.debug(f"{system=}")
        return system

    def _static_response(self, resp: str, stream: bool, **kwargs) -> Message:
        if stream:
            return StreamAgentMessage(content=(e for e in resp), user_id=self.id)
        return AgentMessage(content=resp, user_id=self.id)

    def _dispatch(self, message: UserMessage, **kwargs):
        match_rules = rule_match(query=message.content, match_all=False, regex=True)
        kwargs = copy.deepcopy(kwargs)
        if match_rules:
            func = match_rules[0]["func"]
            kwargs.update(match_rules[0]["kwargs"])
        else:
            func = "chat"

        if func == "static_response":
            return self._static_response(**kwargs)
        elif func == "chat":
            return self._chat(message=message, **kwargs)
        else:
            raise NotImplementedError(f"func {func} not implemented")

    def chat(self, message: UserMessage, stream=False, session_id=None, **kwargs) -> Message | StreamMessage:
        return self._dispatch(message=message, stream=stream, session_id=session_id, **kwargs)

    def _get_memory(self, message: UserMessage) -> str:
        mems = MEM.search(query=message.content, user_id=message.user_id)
        logger.debug(f"get {mems=}")
        mems = [f"{idx}. {mem['text']}" for idx, mem in enumerate(mems, start=1)]
        mems = "可供参考的历史记忆:\n" + "\n".join(mems)
        return mems

    def _chat(self, message: UserMessage, stream=False, session_id=None, recall_memory=False, **kwargs) -> Message | StreamMessage:
        user = Human.from_config(id=message.user_id)
        history = SESSION_MANAGER.get_history(_from=[self.id, message.user_id], to=[self.id, message.user_id], session_id=session_id)
        meta = dict(user_info=user.desc, user_name=user.name, bot_info=self.desc, bot_name=self.name)

        system = self._build_system(user_id=message.user_id)

        user_content = message.content
        if recall_memory:
            mem = self._get_memory(message=message)
            user_content = mem+"\n"+user_content
        message = dict(role="user", content=user_content)
        messages = [dict(role="system", content=system)] + history + [message]

        kwargs["handle_system"] = False

        llm_resp = liteai_api.chat(model=self.model, messages=messages, stream=stream, meta=meta, **kwargs, log_level=LITE_AI_LOG_LEVEL)

        if stream:
            return StreamAgentMessage(content=llm_resp.content, user_id=self.id)
        else:
            return AgentMessage(content=llm_resp.content, user_id=self.id)

    def speak(self, message: Message | str, stream=True, **kwargs) -> Voice:
        speak_config = copy.copy(self.voice_config)
        speak_config.update(**kwargs)

        if isinstance(message, Message):
            text = message.content
        else:
            text = message
        voice = tts(text=text, model="speech-01-turbo", stream=stream, **kwargs)
        return voice

    def get_config(self):
        config = super().get_config()
        config.update(model=self.model)
        return config

    def remember(self, message: Message | StreamMessage):
        if isinstance(message, StreamMessage):
            def _gen():
                acc = ""
                for chunk in message.content:
                    yield chunk
                    acc += chunk
                self.memory.add_message(AgentMessage(content=acc, user_id=self.id))
            return StreamMessage(content=_gen(), user_id=self.id, role=self.role)
        else:
            self.memory.add_message(message)
            return message


class Human(BaseUser):
    role = "user"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    user = Human(agent_info=AgentInfo(name="张三", desc="30岁的男性软件工程师，兴趣包括阅读、徒步和编程", role="user"), memory=None)
    memory = RawMemory(
        history=[
            {
                "role": "agent",
                "content": "你好，我是Emohaa，很高兴见到你。请问有什么我可以帮忙的吗？"
            },
            {
                "role": "user",
                "content": "最近我感觉压力很大，情绪总是很低落。"
            },
            {
                "role": "agent",
                "content": "听起来你最近遇到了不少挑战。可以具体说说是什么让你感到压力大吗？"
            }]
    )
    agent = AIAgent(agent_info=AgentInfo(
        name="Emohaa", desc="Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话", role="agent"), memory=memory)

    resp = agent.chat(message=UserMessage(content="最近我感觉压力很大，情绪总是很低落。", name="张三"))
    print(resp)
