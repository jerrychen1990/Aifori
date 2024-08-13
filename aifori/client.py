#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/17 15:38:54
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import json
import os
from typing import Iterable, List, Tuple
import requests
from aifori.api import decode_chunks
from aifori.core import AssistantMessage, ChatRequest, ChatSpeakRequest, Message, SpeakRequest
from loguru import logger

from liteai.core import Voice
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

    def chat(self, chat_request: ChatRequest, stream=True) -> AssistantMessage:
        data = chat_request.model_dump()
        if stream:
            resp = self._do_request('/assistant/chat_stream', json=data, stream=True).iter_lines()
            assistant_id = data["assistant_id"]

            def gen():
                for chunk in resp:
                    if chunk:
                        chunk = json.loads(chunk.decode('utf-8'))["text_chunk"]
                        yield chunk

            return AssistantMessage(user_id=assistant_id, content=gen())
        else:
            resp = self._do_request('/assistant/chat', json=data)
            return AssistantMessage.model_validate(resp)

    def speak(self, speak_req: SpeakRequest, play=False, local_voice_path: str = None):
        resp = self._do_request('/assistant/speak_stream',
                                json=speak_req.model_dump(), stream=True)
        byte_stream = (json.loads(item.decode("utf-8")) for item in resp.iter_lines())
        byte_stream = (e["voice_chunk"] for e in byte_stream if e.get("voice_chunk"))
        byte_stream = (eval(e) if isinstance(e, str) else e for e in byte_stream)
        voice = build_voice(byte_stream=byte_stream, file_path=local_voice_path)
        if play:
            voice = play_voice(voice)
        return voice

    def chat_speak_stream(self, chat_speak_request: ChatSpeakRequest, local_voice_path: str = None, play: bool = False) -> Tuple[AssistantMessage, Voice]:
        resp = self._do_request('/assistant/chat_speak_stream', json=chat_speak_request.model_dump(), stream=True).iter_lines()
        resp = (json.loads(item.decode("utf-8")) for item in resp)
        # resp = map(lambda e: logger.info(e), resp)

        message, voice = decode_chunks(resp, assistant_id=chat_speak_request.assistant_id,
                                       return_voice=chat_speak_request.return_voice, local_file_path=local_voice_path)
        if play:
            play_voice(voice)
        return message, voice

    def clear_session(self, session_id: str) -> dict:
        resp = self._do_request('/session/clear', json={'session_id': session_id})
        return resp

    def list_messages(self, assistant_id: str,  session_id: str = None, limit: int = 10) -> List[Message]:
        resp = self._do_request('/message/list', json={'assistant_id': assistant_id, 'session_id': session_id, 'limit': limit})
        return [Message.model_validate(message) for message in resp]

    def update_rule(self, rule_path: str) -> str:
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
