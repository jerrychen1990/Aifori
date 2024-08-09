#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/08/07 19:26:26
@Author  :   ChenHao
@Description  :  同步音频、文字的缓冲区
@Contact :   jerrychen1990@gmail.com
'''


class Buffer:
    def __init__(self):
        self.voice_stream = b""
        self.text = ""
        self.text_output_offset = 0
        self.voice_output_offset = 0
        self.tts_output_offset = 0
        self.text_done = False
        self.voice_done = False

    def add_text(self, text: str):
        self.text += text

    def add_voice(self, voice: bytes):
        self.voice_stream += voice

    def gen_tts(self, text_chunk_size=10):
        while not self.text_done:
            while len(self.text) - self.tts_output_offset > text_chunk_size:
                yield dict(text_chunk=self.text[self.tts_output_offset:self.tts_output_offset+text_chunk_size])
                self.tts_output_offset += text_chunk_size
        if self.tts_output_offset < len(self.text):
            yield dict(text_chunk=self.text[self.tts_output_offset:])

    def gen(self, gen_text=True, text_chunk_size=10, gen_voice=False, voice_chunk_size=2048*10):
        while (gen_text and not self.text_done) or (gen_voice and not self.voice_done):
            if gen_text:
                while len(self.text) - self.text_output_offset > text_chunk_size:
                    yield dict(text_chunk=self.text[self.text_output_offset:self.text_output_offset+text_chunk_size])
                    self.text_output_offset += text_chunk_size
            if gen_voice:
                while len(self.voice_stream) - self.voice_output_offset > voice_chunk_size:
                    yield dict(voice_chunk=self.voice_stream[self.voice_output_offset:self.voice_output_offset+voice_chunk_size])
                    self.voice_output_offset += voice_chunk_size

        if gen_text and self.text_output_offset < len(self.text):
            yield dict(text_chunk=self.text[self.text_output_offset:])
        if gen_voice and self.voice_output_offset < len(self.voice_stream):
            yield dict(voice_chunk=self.voice_stream[self.voice_output_offset:])
