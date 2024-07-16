#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/15 17:44:02
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import time
from aifori.tts import tts
import subprocess


mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
mpv_process = subprocess.Popen(
    mpv_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

print(mpv_process)


audio_stream = tts(text="人会有幻觉，大型语言模型也会有幻觉。近日，OpenAI 安全系统团队负责人 Lilian Weng 更新了博客，介绍了近年来在理解、检测和克服 LLM 幻觉方面的诸多研究成果。", stream=True)


audio = b""
for chunk in audio_stream:
    if chunk is not None and chunk != b'\n':
        decoded_hex = chunk
        mpv_process.stdin.write(decoded_hex)  # type: ignore
        mpv_process.stdin.flush()
        audio += decoded_hex


# 结果保存至文件
timestamp = int(time.time())
file_name = f'output_total_{timestamp}.mp3'
with open(file_name, 'wb') as file:
    file.write(audio)
