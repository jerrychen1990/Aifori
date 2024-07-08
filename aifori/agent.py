#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/02 17:07:28
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import os
from typing import Iterable, List
from zhipuai import ZhipuAI
from pydantic import BaseModel
from loguru import logger
from liteai.api import chat


class AgentInfo(BaseModel):
    name: str
    desc: str


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


def chat_llm(user_info: AgentInfo, agent_info: AgentInfo, model: str, messages: List[str], stream=True, **kwargs):
    if model.lower() in ["emohaa", "charglm-3"]:
        return call_lingxin(user_info, agent_info, model, messages, stream=stream)
    else:
        system = f"""你的任务是根据自己的信息，以及用户的信息，提供良好的陪伴服务
你的名字:{agent_info.name}
你的描述:{agent_info.desc}
用户名字: {user_info.name}
用户描述: {user_info.desc}
"""
        messages.insert(0, {"role": "system", "content": system})
        return chat(model=model, messages=messages, stream=stream, **kwargs).content


class Agent:
    def __init__(self, agent_info: AgentInfo):
        self.agent_info = agent_info

    def chat(self, user_info: AgentInfo, model: str, messages: List[str], stream=True, **kwargs) -> Iterable[str]:
        return chat_llm(user_info, self.agent_info, model, messages, stream=stream, **kwargs)


if __name__ == "__main__":
    user_info = AgentInfo(name="张三", desc="30岁的男性软件工程师，兴趣包括阅读、徒步和编程")
    agent_info = AgentInfo(name="Emohaa", desc="Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话")
    messages = [
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
        },
        {
            "role": "user",
            "content": "主要是工作上的压力，任务太多，总感觉做不完。"
        }
    ]
    agent = Agent(agent_info)
    # resp = agent.chat(user_info, "emohaa", messages, stream=False)
    # print(resp)
    resp = agent.chat(user_info, "emohaa", messages, stream=True)
    for item in resp:
        print(item, end="", flush=True)