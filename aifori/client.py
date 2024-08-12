#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/17 15:38:54
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import copy
import itertools
import json
import os
from typing import Iterable, List, Tuple
import requests
from aifori.core import AssistantMessage, ChatRequest, Message, StreamAssistantMessage, Voice
from loguru import logger

from liteai.voice import build_voice, play_voice

# urllib3.disable_warnings()


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

    def create_assistant(self, assistant_id: str, name: str, desc: str, model: str, voice_config: dict = dict()) -> dict:
        data = {'id': assistant_id, 'name': name, 'desc': desc, 'model': model, 'voice_config': voice_config}
        resp = self._do_request('/assistant/create', json=data)
        return resp

    def get_assistant(self, assistant_id: str):
        data = {'id': assistant_id}
        resp = self._do_request('/assistant/get', json=data)
        return resp

    def get_or_create_assistant(self, assistant_id: str, name: str, desc: str, model: str, voice_config: dict = dict()) -> dict:
        try:
            return self.get_assistant(assistant_id)
        except Exception as e:
            return self.create_assistant(assistant_id, name, desc, model, voice_config)

    def delete_assistant(self, assistant_id: str) -> dict:
        data = {'id': assistant_id}
        resp = self._do_request('/assistant/delete', json=data)
        return resp

    def create_user(self, user_id: str, name: str, desc: str) -> dict:
        data = {'id': user_id, 'name': name, 'desc': desc}
        resp = self._do_request('/user/create', json=data)
        return resp

    def get_user(self, user_id: str):
        data = {'id': user_id}
        resp = self._do_request('/user/get', json=data)
        return resp

    def get_or_create_user(self, user_id: str, name: str, desc: str) -> dict:
        try:
            return self.get_user(user_id)
        except Exception as e:
            return self.create_user(user_id, name, desc)

    def delete_user(self, user_id: str) -> dict:
        data = {'id': user_id}
        resp = self._do_request('/user/delete', json=data)
        return resp

    def chat(self, chat_request: ChatRequest, stream=True) -> StreamAssistantMessage | AssistantMessage:
        data = copy.copy(kwargs)
        if stream:
            resp = self._do_request('/assistant/chat_stream', json=data, stream=True).iter_lines()
            assistant_id = data["assistant_id"]

            def gen():
                for chunk in resp:
                    if chunk:
                        chunk = json.loads(chunk.decode('utf-8'))["chunk"]
                        # logger.debug(f"{chunk=}")
                        yield chunk

            return StreamAssistantMessage(user_id=assistant_id, content=gen())
        else:
            resp = self._do_request('/assistant/chat', json=data)
            return AssistantMessage.model_validate(resp)

    def speak(self, assistant_id: str, message: str, voice_config=dict(), max_word=None, play_local=True, dump_path: str = None, chunk_size=1024 * 10):
        message = message if max_word is None else message[:max_word]
        byte_stream: Iterable[bytes] = self._do_request('/assistant/speak_stream',
                                                        json={'assistant_id': assistant_id,
                                                              'message': message, "voice_config": voice_config, "chunk_size": chunk_size}, stream=True)
        byte_stream = byte_stream.iter_content(chunk_size=chunk_size)

        voice = build_voice(byte_stream=byte_stream, file_path=dump_path)

        if play_local:
            voice = play_voice(voice)
        return voice

    def clear_session(self, session_id: str) -> dict:
        resp = self._do_request('/session/clear', json={'session_id': session_id})
        return resp

    def chat_and_speak_stream(self, chat_request: ChatRequest) -> Tuple[StreamAssistantMessage, Voice]:
        resp = self._do_request('/assistant/chat_stream', json=chat_request.model_dump(), stream=True).iter_lines()
        stream = (json.loads(chunk.decode("utf8")) for chunk in resp)
        s1, s2 = itertools.tee(stream)
        text_stream = (e["text_chunk"] for e in s1 if "text_chunk" in e)
        message = StreamAssistantMessage(user_id=chat_request.assistant_id, content=text_stream)

        if chat_request.return_voice:
            voice_stream = (eval(e["voice_chunk"]) for e in s2 if "voice_chunk" in e)
            voice = build_voice(byte_stream=voice_stream)
        else:
            voice = None

        return message, voice

    def list_messages(self, assistant_id: str,  session_id: str = None, limit: int = 10) -> List[Message]:
        resp = self._do_request('/message/list', json={'assistant_id': assistant_id, 'session_id': session_id, 'limit': limit})
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





def handle_chat_stream(stream: Iterable[dict]):
    for chunk in stream:
        k, v = list(chunk.items())[0]
        logger.debug(f"receive chunk with type:{k}, size:{len(v)}, {v[:10]}")
