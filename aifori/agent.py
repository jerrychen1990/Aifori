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
from aifori.config import DEFAULT_SYSTEM_TEMPLATE
from aifori.core import Agent, AgentInfo, AssistantMessage, Message, StreamAssistantMessage, StreamMessage, UserMessage, Voice
from aifori.memory import DBMemory, RawMemory
from aifori.tts import tts
from liteai import api as liteai_api
from aifori.rule import rule_match
from aifori.session import SESSION_MANAGER


class AIAgent(Agent):
    role = "assistant"

    def __init__(self, model: str, voice_config: dict = {}, **kwargs):
        super().__init__(**kwargs)
        self.memory = DBMemory(agent_id=self.id)
        self.model = model
        self.voice_config = voice_config
        self.system_template = DEFAULT_SYSTEM_TEMPLATE

    def _build_system(self, user_id: str) -> str:
        user = HumanAgent.from_config(id=user_id)

        system = self.system_template.format(agent_name=self.name, agent_desc=self.desc, user_name=user.name, user_desc=user.desc)
        logger.debug(f"{system=}")
        return system

    def _static_response(self, resp: str, stream: bool, **kwargs) -> Message:
        if stream:
            return StreamAssistantMessage(content=(e for e in resp), user_id=self.id)
        return AssistantMessage(content=resp, user_id=self.id)

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

    def _chat(self, message: UserMessage, stream=False, session_id=None, **kwargs) -> Message | StreamMessage:
        user = HumanAgent.from_config(id=message.user_id)
        history = SESSION_MANAGER.get_history(_from=[self.id, message.user_id], to=[self.id, message.user_id], session_id=session_id)
        meta = dict(user_info=user.desc, user_name=user.name, bot_info=self.desc, bot_name=self.name)

        system = self._build_system(user_id=message.user_id)

        messages = [dict(role="system", content=system)] + history + [message]
        kwargs["handle_system"] = False

        llm_resp = liteai_api.chat(model=self.model, messages=messages, stream=stream, meta=meta, **kwargs)

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = "user"


# def call_lingxin(user_info: AgentInfo, agent_info: AgentInfo, model: str, messages: List[str], stream=True):
#     api_key = os.environ["ZHIPU_API_KEY"]
#     client = ZhipuAI(api_key=api_key)  # 填写您自己的APIKey
#     meta = dict(user_info=user_info.desc, user_name=user_info.name, bot_info=agent_info.desc, bot_name=agent_info.name)
#     logger.info(f"calling lingxin with: {meta=} {model=} {messages=}, {api_key=}")

#     response = client.chat.completions.create(
#         model=model,  # 填写需要调用的模型名称
#         meta=meta,
#         messages=messages,
#         stream=stream
#     )
#     if not stream:
#         return response.choices[0].message.content
#     else:
#         def _gen():
#             acc = ""
#             for chunk in response:
#                 # print(chunk)
#                 resp = chunk.choices[0].delta.content if chunk.choices[0].delta else ""
#                 if resp:
#                     yield resp
#                     acc += resp
#             logger.debug(f"streaming response :{acc}")
#         return _gen()


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
