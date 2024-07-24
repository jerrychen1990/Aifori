#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/03 11:04:11
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import io
import json
import os
import subprocess
import threading
from time import sleep
from typing import Iterable, Iterator
from gtts import gTTS
import requests
from loguru import logger
from aifori.config import *
from snippets import jdumps, batchify
from pydub import AudioSegment
from pydub.playback import play


def minimax_tts(text: str, model="speech-01-turbo", version="t2a_v2", append=False,
                stream=False, voice_id="tianxin_xiaoling", speed=1, pitch=0) -> bytes:
    group_id = os.environ["MINIMAX_GROUP_ID"]
    api_key = os.environ["MINIMAX_API_KEY"]
    url = f"https://api.minimax.chat/v1/{version}?GroupId={group_id}"

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
        # "pronunciation_dict": {
        #     "tone": ["aifori/(ai4)(fo)(ri)"]
        # },
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
    logger.debug(f"calling minimax tts with payload: {jdumps(payload)}")
    response = requests.request("POST", url, headers=headers, stream=stream, json=payload)
    logger.debug(f"{response.status_code=}")
    response.raise_for_status()
    if not stream:
        data = response.json()
        # logger.info(f"{data=}")
        # print(f"{data=}")
        if "data" not in data:
            logger.exception(data)
            raise Exception(data)
        audio_bytes = bytes.fromhex(data['data']['audio'])
        return audio_bytes
    else:
        def gen():
            for chunk in (response.raw):
                if chunk:
                    if chunk[:5] == b'data:':
                        data = json.loads(chunk[5:])
                        if "data" in data and "extra_info" not in data:
                            if "audio" in data["data"]:
                                audio = data["data"]['audio']
                                yield bytes.fromhex(audio)
        return gen()


def get_md5(text):
    import hashlib
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()


def tts(text: str | Iterable[str], provider="minimax", tgt_path=None, stream=False, **kwargs):
    if not tgt_path:
        tgt_path = os.path.join(VOICE_DIR, provider, get_md5(text) + ".mp3")
    os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
    logger.debug(f"{provider=}, {kwargs=}")
    if provider == "minimax":
        bytes = minimax_tts(text, stream=stream, **kwargs)
        if not stream:
            with open(tgt_path, "wb") as f:
                f.write(bytes)
            return tgt_path
        else:
            return bytes
    else:
        raise Exception(f"Unknown provider: {provider}")


class TTSStreamThread(threading.Thread):
    def __init__(self, text: str | Iterable[str], provider="minimax", input_chunk_size=16, output_chunks_size=32, wait_time=0.5, ** kwargs):
        super().__init__()
        self.text = text
        self.provider = provider
        self.input_chunk_size = input_chunk_size
        self.output_chunks_size = output_chunks_size
        self.kwargs = kwargs
        self.audio_stream = io.BytesIO()
        self._stop_event = threading.Event()
        self.read_start = 0
        self.wait_time = wait_time
        self.lock = threading.Lock()

    def run(self):
        if isinstance(self.text, str):
            text_stream = list(self.text)
        else:
            text_stream = self.text

        for batch in batchify(text_stream, self.input_chunk_size):
            logger.debug(f"calling tts_stream with batch: {batch}")
            batch = "".join(batch)
            with self.lock:
                if self.provider == "minimax":
                    batch_voice = minimax_tts(batch, stream=True, **self.kwargs)
                    for item in batch_voice:
                        self.audio_stream.write(item)
                elif self.provider == "google":
                    tts = gTTS(self.text)
                    tts.write_to_fp(self.audio_stream)
                else:
                    raise Exception(f"Unknown provider: {self.provider}")

        logger.debug("tts stream finished")
        self._stop_event.set()

    def stop(self):
        logger.info("stopping tts stream")
        self._stop_event.set()

    def yield_audio_bytes(self):
        # self.audio_stream.seek(0)
        while True:
            with self.lock:
                # logger.debug(f"reading from :{self.read_start}")
                self.audio_stream.seek(self.read_start)
                chunk = self.audio_stream.read(self.output_chunks_size)
                self.read_start = self.audio_stream.tell()

                # logger.info(f"yielding chunk {chunk}")
                if not chunk:
                    if self._stop_event.is_set():
                        break
                    else:
                        # logger.debug("no new chunk, waiting")
                        sleep(self.wait_time)
                        continue
                yield chunk
        logger.info("read tts stream ended")


def tts_stream(text: str | Iterable[str], provider="minimax", input_chunk_size=32, output_chunks_size=1024 * 10, wait_time=.5, **kwargs) -> Iterator[str]:

    tts_thread = TTSStreamThread(text=text, provider=provider, input_chunk_size=input_chunk_size,
                                 output_chunks_size=output_chunks_size, wait_time=wait_time, ** kwargs)
    tts_thread.start()
    yield from tts_thread.yield_audio_bytes()


mpv_process = None


def get_play_process():
    global mpv_process
    if not mpv_process:
        mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
        mpv_process = subprocess.Popen(
            mpv_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return mpv_process


def play_voice(voice_stream: Iterable[bytes] | str):
    if isinstance(voice_stream, str):
        assert voice_stream.endswith(".mp3")
        # 加载 mp3 文件
        song = AudioSegment.from_mp3(voice_stream)

        # 播放
        play(song)
        return voice_stream
    else:

        process = get_play_process()
        rs_voice_stream = list()

        audio = b""
        for chunk in voice_stream:
            if chunk is not None and chunk != b'\n':
                decoded_hex = chunk
                # logger.debug(f"flush {len(decoded_hex)} bytes to play")
                process.stdin.write(decoded_hex)  # type: ignore
                process.stdin.flush()
                audio += decoded_hex
                rs_voice_stream.append(chunk)
        return rs_voice_stream


def dump_voice(voice_stream: Iterable[bytes], path: str):
    rs_voice_stream = list()

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        for chunk in voice_stream:
            if chunk is not None and chunk != b'\n':
                decoded_hex = chunk
                f.write(decoded_hex)
                rs_voice_stream.append(decoded_hex)
    return rs_voice_stream


if __name__ == "__main__":
    path = tts("你好呀，我是小白")
    print(path)
