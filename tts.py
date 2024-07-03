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
from config import *


def minimax_tts(text, tgt_path, model="speech-01-turbo", voice_id="male-qn-qingse", speed=1, pitch=0):
    group_id = os.getenv("MINIMAX_GROUP_ID")
    api_key = os.getenv("MINIMAX_API_KEY")
    # print(group_id)
    # print(api_key)
    url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={group_id}"

    payload = json.dumps({
        "model": model,
        "text": text,
        "stream": False,
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
    })
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # print(payload)

    response = requests.request("POST", url, stream=True, headers=headers, data=payload)
    response.raise_for_status()

    data = response.json()
    # print(data)
    # 获取audio字段的值
    if "data" not in data:
        raise Exception(data)
    audio_value = bytes.fromhex(data['data']['audio'])
    with open(tgt_path, 'wb') as f:
        f.write(audio_value)

# get md5 of text


def get_md5(text):
    import hashlib
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()


def tts(text, provider="minimax", tgt_path=None, **kwargs):
    if not tgt_path:
        tgt_path = os.path.join(voice_dir, provider, get_md5(text) + ".mp3")
    os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
    if provider == "minimax":
        minimax_tts(text, tgt_path=tgt_path, **kwargs)
    return tgt_path


if __name__ == "__main__":
    path = tts("你好呀，我是小白")
    print(path)
