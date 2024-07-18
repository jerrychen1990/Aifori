#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/17 15:38:54
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import json
import requests
from aifori.core import AssistantMessage, StreamAssistantMessage
from loguru import logger

from aifori.tts import play_voice


class AiForiClient(object):
    def __init__(self, host: str):
        self.host = host

    def _do_request(self, path, method="post", json=dict(), stream=False):
        url = f"{self.host}/{path}"
        logger.debug(f"{method.upper()} to {url} with {json=}, stream={stream}")
        resp = requests.request(method, url, json=json, stream=stream)
        resp.raise_for_status()
        if not stream:
            if resp.json()["code"] != 200:
                raise Exception(resp.json()["msg"])
            logger.debug(f"resp: {resp.json()}")
            return resp.json()["data"]

        return resp

    def check_health(self) -> bool:
        resp = self._do_request("health", method="get")
        assert resp["status"].upper() == "OK"

    def create_agent(self, agent_id: str, name: str, desc: str, model: str, voice_config: dict = dict()) -> dict:
        data = {'agent_id': agent_id, 'name': name, 'desc': desc, 'model': model, 'voice_config': voice_config}
        resp = self._do_request('/agent/create', json=data)
        return resp

    def chat(self, agent_id: str, user_id: str, message: str, do_remember=True, stream=True) -> StreamAssistantMessage | AssistantMessage:
        data = {'id': agent_id,
                'user_id': user_id, 'message': message, 'do_remember': do_remember}
        if stream:
            resp = self._do_request('/agent/chat_stream', json=data, stream=True).iter_lines()
            assistant_id = json.loads(next(resp).decode('utf-8'))["assistant_id"]
            logger.debug(f"{assistant_id=}")

            def gen():
                for chunk in resp:
                    if chunk:
                        chunk = json.loads(chunk.decode('utf-8'))["chunk"]
                        # logger.debug(f"{chunk=}")
                        yield chunk

            return StreamAssistantMessage(id=assistant_id, content=gen())
        else:
            resp = self._do_request('/agent/chat', json=data)
            return AssistantMessage.model_validate(resp)

    def speak(self, agent_id: str, message: str, tts_config=dict(), max_word=None):
        message = message if max_word is None else message[:max_word]
        voice = self._do_request('/agent/speak_stream', json={'id': agent_id,
                                                              'message': message, "tts_config": tts_config}, stream=True)
        logger.debug(f"{voice=}")
        play_voice(voice)
        return voice

    def chat_and_speak(self, agent_id: str, user_id: str, message: str, tts_config=dict(), do_remember=True, max_word=None) -> AssistantMessage:
        message = self.chat(agent_id, user_id, message, stream=False, do_remember=do_remember)
        self.speak(agent_id, message=message.content, tts_config=tts_config, max_word=max_word)
