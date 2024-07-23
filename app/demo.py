#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/02 17:24:15
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import os
import uuid
import streamlit as st

from aifori.client import AiForiClient
from aifori.config import VOICE_DIR
from aifori.tts import dump_voice
from snippets import set_logger
from app.config import *


print("reload")
HOST = "http://127.0.0.1:9001"

st.set_page_config(page_title="AIFori", page_icon="🤖", layout="wide")

with st.sidebar.expander("Agent信息配置"):
    user_name = st.text_input("用户名", DEFAULT_USER_NAME)
    user_desc = st.text_area("用户描述", DEFAULT_USER_DESC, height=100)

    ai_name = st.text_input("AI名称", DEFAULT_AI_NAME)
    ai_desc = st.text_area("用户描述", DEFAULT_AI_DESC, height=100)

model = st.sidebar.selectbox("模型", LLM_MODELS)

with st.sidebar.expander("音色配置"):
    character = st.selectbox("音色", CHARACTER_MAP.keys())
    voice_id = CHARACTER_MAP[character]["voice_id"]
    speed = st.slider("语速", 0.5, 2.0, 1.0)
    pitch = st.slider("音调", -12, 12, 0, 1)

clear = st.sidebar.button("新一轮对话")
autoplay = st.sidebar.checkbox("自动播放", value=False)


class SessionManager:
    # logger = set_logger("DEV", __name__)

    def __init__(self) -> None:
        print("setting logger")

        self.logger = set_logger("DEV", __name__)
        self.refresh()

    def refresh(self):
        self.logger.info("refresh session manager")
        self.client = AiForiClient(host=HOST)
        self.session_info = dict(agent_id=str(uuid.uuid4()), session_id=str(uuid.uuid4()), user_id=str(uuid.uuid4()))
        self.agent_id = self.session_info["agent_id"]
        self.session_id = self.session_info["session_id"]
        self.user_id = self.session_info["user_id"]

        self.round = 0
        self.voice_config = dict(voice_id=voice_id, speed=speed, pitch=pitch)
        self.agent_info = self.client.create_agent(agent_id=self.agent_id, name=ai_name, desc=ai_desc,
                                                   model=model, voice_config=self.voice_config)

        self.user_info = self.client.create_agent(agent_id=self.agent_id, name=ai_name, desc=ai_desc,
                                                  model=model, voice_config=self.voice_config)
        self.messages = []

    def get_resp(self, prompt):
        resp = self.client.chat(message=prompt, **self.session_info, stream=True)
        return resp.content

    def play_message(self, message: str, tts_config):
        voice_path = os.path.join(VOICE_DIR, self.session_id, f"{self.round}.mp3")
        self.client.speak(message=message, agent_id=self.agent_id, callbacks=[[dump_voice, dict(path=voice_path)]], tts_config=tts_config)
        return voice_path

    def add_message(self, message):
        self.logger.info(f"add message: {message}")
        self.messages.append(message)


if not st.session_state.get("session_manager"):
    print("setting session manager")
    session_manager = SessionManager()
    st.session_state.session_manager = session_manager
    # st.session_state["session_manager"] = 1


# st.info(f"{st.session_state.get('session_manager')=}")

session_manager: SessionManager = st.session_state.session_manager

if clear:
    session_manager.refresh()

# Accept user input
for message in session_manager.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("你好，你是谁？"):
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

    resp = session_manager.get_resp(prompt)
    for token in resp:
        full_response += token
        # st.info(full_response)
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    tts_config = dict(voice_id=voice_id, speed=speed, pitch=pitch)
    voice_path = session_manager.play_message(full_response, tts_config=tts_config)
    st.audio(voice_path, format='audio/mp3', autoplay=autoplay)

    user_message = {"role": "user", "content": prompt, "session_id": session_manager.session_id}
    assistant_message = {"role": "assistant", "content": full_response, "session_id": session_manager.session_id, "voice_path": voice_path}

    session_manager.add_message(user_message)
    session_manager.add_message(assistant_message)

    session_manager.round += 1
