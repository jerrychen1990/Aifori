#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/02 17:07:28
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import copy
import os
from typing import List
from loguru import logger
from aifori.core import Agent, AgentInfo, AssistantMessage, Message, StreamAssistantMessage, StreamMessage, UserMessage, Voice
from aifori.memory import DBMemory, RawMemory
from aifori.tts import tts
from liteai.api import chat
from aifori.session import SESSION_MANAGER
from snippets import load
from zhipuai import ZhipuAI


class AIAgent(Agent):
    def __init__(self, model: str, voice_config: dict = {}, **kwargs):
        super().__init__(**kwargs)
        self.role = "assistant"
        self.memory = DBMemory(agent_id=self.id)
        self.model = model
        self.voice_config = voice_config

    def chat(self, message: UserMessage, stream=False, session_id=None, **kwargs) -> Message | StreamMessage:
        # history = self.memory.to_llm_messages()
        history = SESSION_MANAGER.get_history(related_ids=[self.id, message.user_id], session_id=session_id)

        system = f"""
你是一个善解人意的聊天机器人，你的名字叫:{self.name}
你的人设是:{self.desc}
请简短、温和地和用户对话
"""

        messages = [dict(role="system", content=system)] + history + [message]

        llm_resp = chat(model=self.model, messages=messages, stream=stream, **kwargs)

        if stream:
            return StreamAssistantMessage(content=llm_resp.content, user_id=self.id)
        else:
            return AssistantMessage(content=llm_resp.content, user_id=self.id)

    def speak(self, message: Message | str, stream=True, **kwargs) -> Voice:
        speak_config = copy.copy(self.voice_config)
        speak_config.update(**kwargs)

        if isinstance(message, Message):
            text = message.content
        else:
            text = message

        voice_stream = tts(text=text, stream=stream, **speak_config)
        return Voice(content=voice_stream)

    def get_config(self):
        config = super().get_config()
        config.update(model=self.model)
        return config

    @classmethod
    def from_config(cls, path: str):
        data = load(path)
        logger.debug(f"load agent from {path}")
        return cls(**data)

    def remember(self, message: Message | StreamMessage):
        if isinstance(message, StreamMessage):
            def _gen():
                acc = ""
                for chunk in message.content:
                    yield chunk
                    acc += chunk
                self.memory.add_message(AssistantMessage(content=acc, user_id=self.id))
            return StreamMessage(content=_gen(), user_id=self.id, role=self.role)
        else:
            self.memory.add_message(message)
            return message


class HumanAgent(Agent):
    pass


def call_lingxin(user_info: AgentInfo, agent_info: AgentInfo, model: str, messages: List[str], stream=True):
    api_key = os.environ["ZHIPU_API_KEY"]
    client = ZhipuAI(api_key=api_key)  # 填写您自己的APIKey
    meta = dict(user_info=user_info.desc, user_name=user_info.name, bot_info=agent_info.desc, bot_name=agent_info.name)
    logger.info(f"calling lingxin with: {meta=} {model=} {messages=}, {api_key=}")

    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        meta=meta,
        messages=messages,
        stream=stream
    )
    if not stream:
        return response.choices[0].message.content
    else:
        def _gen():
            acc = ""
            for chunk in response:
                # print(chunk)
                resp = chunk.choices[0].delta.content if chunk.choices[0].delta else ""
                if resp:
                    yield resp
                    acc += resp
            logger.debug(f"streaming response :{acc}")
        return _gen()


# def chat_llm(user_info: AgentInfo, agent_info: AgentInfo, model: str, messages: List[str], stream=True, **kwargs):
#     if model.lower() in ["emohaa", "charglm-3"]:
#         return call_lingxin(user_info, agent_info, model, messages, stream=stream)
#     else:
#         system = f"""你的任务是根据自己的信息，以及用户的信息，提供良好的陪伴服务
# 你的名字:{agent_info.name}
# 你的描述:{agent_info.desc}
# 用户名字: {user_info.name}
# 用户描述: {user_info.desc}
# """
#         messages.insert(0, {"role": "system", "content": system})
#         return chat(model=model, messages=messages, stream=stream, **kwargs).content

if __name__ == "__main__":
    user = HumanAgent(agent_info=AgentInfo(name="张三", desc="30岁的男性软件工程师，兴趣包括阅读、徒步和编程", role="user"), memory=None)
    memory = RawMemory(
        history=[
            {
                "role": "assistant",
                "content": "你好，我是Emohaa，很高兴见到你。请问有什么我可以帮忙的吗？"
            },
            {
                "role": "user",
                "content": "最近我感觉压力很大，情绪总是很低落。"
            },
            {
                "role": "assistant",
                "content": "听起来你最近遇到了不少挑战。可以具体说说是什么让你感到压力大吗？"
            }]
    )
    assistant = AIAgent(agent_info=AgentInfo(
        name="Emohaa", desc="Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话", role="assistant"), memory=memory)

    resp = assistant.chat(message=UserMessage(content="最近我感觉压力很大，情绪总是很低落。", name="张三"))
    print(resp)
