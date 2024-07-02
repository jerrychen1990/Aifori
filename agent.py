#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/02 17:07:28
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import os
from pyexpat.errors import messages
from typing import Iterable, List
from zhipuai import ZhipuAI
from pydantic import BaseModel


class AgentInfo(BaseModel):
    name: str
    desc: str


def chat_llm(user_info: AgentInfo, agent_info: AgentInfo, model, messages: List[str], stream=True):
    client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY"))  # 填写您自己的APIKey
    meta = dict(user_info=user_info.desc, user_name=user_info.name, bot_info=agent_info.desc, bot_name=agent_info.name)

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
            for chunk in response:
                # print(chunk)
                yield chunk.choices[0].delta.content if chunk.choices[0].delta else ""
        return _gen()

    return response


class Agent:
    def __init__(self, agent_info: AgentInfo):
        self.agent_info = agent_info

    def chat(self, user_info: AgentInfo, model: str, messages: List[str], stream=True) -> Iterable[str]:
        return chat_llm(user_info, self.agent_info, model, messages, stream=stream)


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
