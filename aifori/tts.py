#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/03 11:04:11
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import json
import os
import requests
from loguru import logger
from aifori.config import *
from snippets import jdumps


def minimax_tts(text, tgt_path, model="speech-01-turbo",
                stream=False, voice_id="male-qn-qingse", speed=1, pitch=0):
    group_id = os.environ["MINIMAX_GROUP_ID"]
    api_key = os.environ["MINIMAX_API_KEY"]
    # print(group_id)
    # print(api_key)
    url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={group_id}"

    payload = {
        "model": model,
        "text": text,
        "stream": stream,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": 1,
            "pitch": pitch
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # print(payload)
    logger.info(f"calling minimax tts with payload: {jdumps(payload)}")

    response = requests.request("POST", url, headers=headers, stream=stream, json=payload)
    response.raise_for_status()
    if not stream:
        data = response.json()
        # logger.info(f"{data=}")
        # print(f"{data=}")
        if "data" not in data:
            logger.exception(data)
            raise Exception(data)
        audio_value = bytes.fromhex(data['data']['audio'])
        with open(tgt_path, 'wb') as f:
            f.write(audio_value)
        return tgt_path
    else:
        def gen():
            for chunk in (response.raw):
                if chunk:
                    # print(chunk)
                    if chunk[:5] == b'data:':
                        data = json.loads(chunk[5:])
                        if "data" in data and "extra_info" not in data:
                            if "audio" in data["data"]:
                                audio = data["data"]['audio']
                                yield bytes.fromhex(audio)
        return gen()


# get md5 of text


def get_md5(text):
    import hashlib
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()


def tts(text, provider="minimax", tgt_path=None, **kwargs):
    if not tgt_path:
        tgt_path = os.path.join(VOICE_DIR, provider, get_md5(text) + ".mp3")
    os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
    logger.info(f"{provider=}, {kwargs=}")
    if provider == "minimax":
        minimax_tts(text, tgt_path=tgt_path, **kwargs)
    return tgt_path


if __name__ == "__main__":
    path = tts("你好呀，我是小白")
    print(path)