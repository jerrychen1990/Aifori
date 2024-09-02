#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/17 15:38:54
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import itertools
import json
import os
from typing import Callable, Dict, Iterable, List, Tuple
import requests
from aifori.core import AssistantMessage, ChatRequest, ChatSpeakRequest, Message, SpeakRequest
from loguru import logger

from liteai.core import ToolCall, Voice
from liteai.voice import build_voice, play_voice
from snippets import jdumps
from cachetools import LRUCache, cached
from requests.auth import HTTPBasicAuth


# urllib3.disable_warnings()


def handle_chat_stream(stream: Iterable[dict]):
    for chunk in stream:
        k, v = list(chunk.items())[0]
        logger.debug(f"receive chunk with type:{k}, size:{len(v)}, {v[:10]}")


def decode_message(stream: Iterable[dict | bytes], assistant_id: str) -> AssistantMessage:
    dict_stream = (e if isinstance(e, dict) else eval(e.decode("utf8")) for e in stream)
    content_stream, tool_stream = itertools.tee(dict_stream)
    content_stream = (e["text_chunk"] for e in content_stream if "text_chunk" in e)
    tool_calls = []
    for tool in tool_stream:
        if "tool_call" in tool:
            tool_call = json.loads(tool["tool_call"])
            logger.debug(f"decode tool call: {tool_call}")
            tool_calls.append(ToolCall.model_validate(tool_call))

    return AssistantMessage(user_id=assistant_id, content=content_stream, tool_calls=tool_calls)


def decode_voice(byte_stream: Iterable[dict | bytes], local_file_path: str) -> Voice:
    byte_stream = (e if isinstance(e, dict) else eval(e.decode("utf8")) for e in byte_stream)
    voice_stream = (e["voice_chunk"] for e in byte_stream if e.get("voice_chunk"))
    voice_stream = (eval(e) if isinstance(e, str) else e for e in voice_stream)
    logger.debug(f"decode voice with {local_file_path=}")
    voice = build_voice(byte_stream=voice_stream, file_path=local_file_path)
    return voice


def decode_chunks(chunks: Iterable[dict], assistant_id: str, return_voice: bool, local_file_path: str) -> Tuple[AssistantMessage, Voice]:
    s1, s2 = itertools.tee(chunks)
    message = decode_message(s1, assistant_id)
    if return_voice:
        voice = decode_voice(s2, local_file_path)
    else:
        voice = None
    return message, voice


class AiForiClient(object):
    def __init__(self, host: str, username: str = "", password: str = ""):
        self.host = host
        if username and password:
            self.auth = HTTPBasicAuth(username, password)
        else:
            self.auth = None

    def _do_request(self, path, method="post", _json=dict(), stream=False, files=dict()):
        url = f"{self.host}{path}"
        logger.debug(f"{method.upper()} to {url} with json=\n{jdumps(_json)}, {files=}, {stream=}")
        if _json:
            resp = requests.request(method, url, json=_json, stream=stream, verify=False, auth=self.auth)
        else:
            resp = requests.request(method, url, files=files, stream=stream, verify=False, auth=self.auth)
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
        resp = self._do_request('/assistant/create', _json=data)
        return resp

    @cached(LRUCache(maxsize=128))
    def get_assistant(self, assistant_id: str):
        data = {'id': assistant_id}
        resp = self._do_request('/assistant/get', _json=data)
        return resp

    def get_or_create_assistant(self, assistant_id: str, name: str, desc: str, model: str, voice_config: dict = dict()) -> dict:
        try:
            return self.get_assistant(assistant_id)
        except Exception as e:
            return self.create_assistant(assistant_id, name, desc, model, voice_config)

    def delete_assistant(self, assistant_id: str) -> dict:
        data = {'id': assistant_id}
        resp = self._do_request('/assistant/delete', _json=data)
        return resp

    def create_user(self, user_id: str, name: str, desc: str) -> dict:
        data = {'id': user_id, 'name': name, 'desc': desc}
        resp = self._do_request('/user/create', _json=data)
        return resp

    @cached(LRUCache(maxsize=128))
    def get_user(self, user_id: str):
        data = {'id': user_id}
        resp = self._do_request('/user/get', _json=data)
        return resp

    def get_or_create_user(self, user_id: str, name: str, desc: str) -> dict:
        try:
            return self.get_user(user_id)
        except Exception as e:
            return self.create_user(user_id, name, desc)

    def delete_user(self, user_id: str) -> dict:
        data = {'id': user_id}
        resp = self._do_request('/user/delete', _json=data)
        return resp

    def chat(self, chat_request: ChatRequest, stream=True) -> AssistantMessage:
        data = chat_request.model_dump()
        if stream:
            resp = self._do_request('/assistant/chat_stream', _json=data, stream=True).iter_lines()
            assistant_id = data["assistant_id"]
            return decode_message(resp, assistant_id)
        else:
            resp = self._do_request('/assistant/chat', _json=data)
            return AssistantMessage.model_validate(resp)

    def speak(self, speak_req: SpeakRequest, play=False, local_voice_path: str = None) -> Voice:
        resp = self._do_request('/assistant/speak_stream',
                                _json=speak_req.model_dump(), stream=True).iter_lines()
        voice = decode_voice(resp, local_voice_path)
        if play:
            play_voice(voice)
        return voice

    def chat_speak_stream(self, chat_speak_request: ChatSpeakRequest, local_voice_path: str = None, play: bool = False) -> Tuple[AssistantMessage, Voice]:
        resp = self._do_request('/assistant/chat_speak_stream', _json=chat_speak_request.model_dump(), stream=True).iter_lines()
        resp = (json.loads(item.decode("utf-8")) for item in resp)
        message, voice = decode_chunks(resp, assistant_id=chat_speak_request.assistant_id,
                                       return_voice=chat_speak_request.return_voice, local_file_path=local_voice_path)
        if play:
            play_voice(voice)
        return message, voice

    def play_music(self, user_id: str, music_desc: str, local_voice_path: str = None, play: bool = True, max_seconds=None) -> Voice:
        resp = self._do_request('/assistant/play_music_stream', _json=dict(user_id=user_id, music_desc=music_desc), stream=True).iter_lines()
        voice = decode_voice(resp, local_voice_path)
        if play:
            play_voice(voice, max_seconds=max_seconds)
        return voice

    def on_play_music(self, message, tool_call, **kwargs):
        logger.debug(f"play music with {tool_call=}, {kwargs=}")
        new_kwargs = dict(**tool_call.parameters, **kwargs)
        logger.debug(f"play music with {new_kwargs=}")
        self.play_music(**new_kwargs)

    def on_tool(self, message: AssistantMessage, callbacks=Dict[str, Callable], **kwargs):
        if tool_calls := message.tool_calls:
            for tool_call in tool_calls:
                if tool_call.name in callbacks:
                    logger.debug(f"on tool call: {tool_call}")
                    callbacks[tool_call.name](message=message, tool_call=tool_call, **kwargs)

    def clear_session(self, session_id: str) -> dict:
        resp = self._do_request('/session/clear', _json={'session_id': session_id})
        return resp

    def list_messages(self, assistant_id: str,  session_id: str = None, limit: int = 10) -> List[Message]:
        resp = self._do_request('/message/list', _json={'assistant_id': assistant_id, 'session_id': session_id, 'limit': limit})
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
