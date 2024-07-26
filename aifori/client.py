#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/17 15:38:54
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import copy
import json
import os
import time
from typing import List, Tuple
import requests
from aifori.core import AssistantMessage, Message, StreamAssistantMessage, Voice
from loguru import logger

from aifori.tts import dump_voice, play_voice
import urllib3

urllib3.disable_warnings()


class AiForiClient(object):
    def __init__(self, host: str):
        self.host = host

    def _do_request(self, path, method="post", json=dict(), stream=False, files=dict()):
        url = f"{self.host}{path}"
        logger.debug(f"{method.upper()} to {url} with {json=}, {files=}, {stream=}")
        if json:
            resp = requests.request(method, url, json=json, stream=stream, verify=False)
        else:
            resp = requests.request(method, url, files=files, stream=stream, verify=False)
        resp.raise_for_status()
        if not stream:
            if resp.json()["code"] != 200:
                raise Exception(resp.json()["msg"])
            logger.debug(f"resp: {resp.json()}")
            return resp.json()["data"]

        return resp

    def check_health(self) -> bool:
        resp = self._do_request("/health", method="get")
        assert resp["status"].upper() == "OK"

    def create_agent(self, agent_id: str, name: str, desc: str, model: str, voice_config: dict = dict()) -> dict:
        data = {'id': agent_id, 'name': name, 'desc': desc, 'model': model, 'voice_config': voice_config}
        resp = self._do_request('/agent/create', json=data)
        return resp

    def create_user(self, user_id: str, name: str, desc: str) -> dict:
        data = {'id': user_id, 'name': name, 'desc': desc}
        resp = self._do_request('/user/create', json=data)
        return resp

    def delete_agent(self, agent_id: str) -> dict:
        data = {'id': agent_id}
        resp = self._do_request('/agent/delete', json=data)
        return resp

    def delete_user(self, user_id: str) -> dict:
        data = {'id': user_id}
        resp = self._do_request('/user/delete', json=data)
        return resp

    def chat(self,  stream=True, **kwargs) -> StreamAssistantMessage | AssistantMessage:
        data = copy.copy(kwargs)
        st = time.time()
        perf = dict()
        if stream:
            resp = self._do_request('/agent/chat_stream', json=data, stream=True).iter_lines()
            assistant_id = json.loads(next(resp).decode('utf-8'))["assistant_id"]
            # logger.debug(f"{assistant_id=}")

            def gen():
                for chunk in resp:
                    if chunk:
                        chunk = json.loads(chunk.decode('utf-8'))["chunk"]
                        # logger.debug(f"{chunk=}")
                        yield chunk

            return StreamAssistantMessage(user_id=assistant_id, content=gen())
        else:
            resp = self._do_request('/agent/chat', json=data)
            return AssistantMessage.model_validate(resp)

    def speak(self, agent_id: str, message: str, voice_config=dict(), max_word=None, play_local=True, dump_path=None):
        message = message if max_word is None else message[:max_word]
        voice = self._do_request('/agent/speak_stream', json={'agent_id': agent_id,
                                                              'message': message, "voice_config": voice_config}, stream=True)

        if play_local:
            voice = play_voice(voice)
        if dump_path:
            voice = dump_voice(voice, dump_path)

        return voice

    def clear_session(self, session_id: str) -> dict:
        resp = self._do_request('/session/clear', json={'session_id': session_id})
        return resp

    def chat_and_speak(self, session_id: str, agent_id: str, user_id: str, message: str, voice_config=dict(),
                       do_remember=True, max_word=None, play_local=True, dump_path: str = None) -> Tuple[AssistantMessage, Voice]:
        resp_message: Message = self.chat(agent_id=agent_id, user_id=user_id, message=message,
                                          stream=False, do_remember=do_remember, session_id=session_id)
        logger.debug(f"{resp_message=}")
        voice = self.speak(agent_id, message=resp_message.content, voice_config=voice_config,
                           max_word=max_word, play_local=play_local, dump_path=dump_path)
        return resp_message, voice

    def list_messages(self, agent_id: str,  session_id: str = None, limit: int = 10) -> List[Message]:
        resp = self._do_request('/message/list', json={'agent_id': agent_id, 'session_id': session_id, 'limit': limit})
        return [Message.model_validate(message) for message in resp]

    def update_rule(self, rule_path) -> str:
        if not os.path.exists(rule_path):
            raise FileNotFoundError(f"{rule_path} not found")
        if not rule_path.endswith(".jsonl"):
            raise ValueError(f"{rule_path} must be a jsonline file")

        with open(rule_path, "rb") as f:
            files = {'upload_file': (os.path.basename(rule_path), f)}
            resp = self._do_request('/rule/update', files=files)
            return resp
