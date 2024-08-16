#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/02 17:24:15
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import base64
import io
import os
import time
import uuid
import streamlit as st

from aifori.client import AiForiClient
from aifori.config import *
from aifori.core import ChatRequest, SpeakRequest
from liteai.core import Voice
from liteai.voice import get_duration
from snippets import set_logger, load, dump
from app.config import *


print("reload")

st.set_page_config(page_title="AIFori", page_icon="🤖", layout="wide")


class SessionManager:
    # logger = set_logger("DEV", __name__)

    def __init__(self) -> None:
        print("setting logger")

        self.logger = set_logger("DEV", __name__)
        self.client = AiForiClient(host=HOST)
        self.new_session()

    def update_profile(self, assistant_id, assistant_name, assistant_desc, user_id, user_name, user_desc, model, voice_config):
        logger.debug("updating profile")
        self.assistant_info = self.client.get_or_create_assistant(assistant_id=assistant_id, name=assistant_name, desc=assistant_desc,
                                                                  model=model, voice_config=voice_config)
        self.assistant_id = assistant_id

        self.user_info = self.client.get_or_create_user(user_id=user_id, name=user_name, desc=user_desc)
        self.user_id = user_id

    def new_session(self):
        self.session_id = str(uuid.uuid4())
        self.messages = []
        self.round = 0

    def get_resp(self, prompt):
        req = ChatRequest(message=prompt, user_id=self.user_id, assistant_id=self.assistant_id, session_id=self.session_id)
        resp = self.client.chat(req, stream=True)
        return resp.content

    def message2voice(self, message: str, voice_config):
        local_voice_path = os.path.join(VOICE_DIR, self.session_id, f"{self.round}.mp3")
        speak_req = SpeakRequest(message=message, assistant_id=self.assistant_id, session_id=self.session_id,
                                 voice_config=voice_config, voice_chunk_size=VOICE_CHUNK_SIZE)
        voice = self.client.speak(speak_req, local_voice_path=local_voice_path)
        return voice

    def add_message(self, message):
        self.logger.info(f"add message: {message}")
        self.messages.append(message)


if not st.session_state.get("session_manager"):
    print("setting session manager")
    session_manager = SessionManager()
    st.session_state.session_manager = session_manager

session_manager: SessionManager = st.session_state.session_manager


profiles = load(PROFILE_PATH)
profile_options = list(profiles.items()) + [("新建Agent", None)] + [("临时对话", None)]
p_name, profile = st.sidebar.selectbox(label="Agent列表", index=0, options=profile_options, format_func=lambda x: x[0])
logger.info(f"{p_name=}, {profile=}")

if not profile:
    with st.sidebar.expander("新建Agent", expanded=True):
        user_name = st.text_input("用户名", DEFAULT_USER_NAME)
        user_desc = st.text_area("用户描述", DEFAULT_USER_DESC, height=100)

        assistant_name = st.text_input("AI名称", DEFAULT_AI_NAME)
        assistant_desc = st.text_area("用户描述", DEFAULT_AI_DESC, height=100)
        profile = dict(user_name=user_name,  user_desc=user_desc,
                       assistant_desc=assistant_desc, assistant_name=assistant_name)

        if p_name == "新建Agent":
            profile.update(user_id=user_name, assistant_id=assistant_name)
        else:
            profile.update(user_id=str(uuid.uuid4()), assistant_id=str(uuid.uuid4()))

        if p_name == "新建Agent":
            save = st.button("保存")
            if save:
                p_key = f"{assistant_name}_{user_name}"
                if p_key in profiles:
                    st.warning("无法更新Agent配置，已有重复的Agent+User组合!")
                else:
                    profiles[p_key] = profile
                dump(profiles, PROFILE_PATH)
                st.rerun()


model = st.sidebar.selectbox("模型", LLM_MODELS)
with st.sidebar.expander("音色配置"):
    character = st.selectbox("音色", CHARACTER_MAP.keys())
    voice_id = CHARACTER_MAP[character]["voice_id"]
    speed = st.slider("语速", 0.5, 2.0, 1.0)
    pitch = st.slider("音调", -12, 12, 0, 1)

voice_config = dict(voice_id=voice_id, speed=speed, pitch=pitch)
session_manager.update_profile(**profile, model=model, voice_config=voice_config)


clear = st.sidebar.button("新一轮对话")
speak = st.sidebar.checkbox("播放音频", value=False)
# if speak:
#     autoplay = st.sidebar.checkbox("自动播放", value=False)


if clear:
    st.info("重置会话")
    session_manager = SessionManager()
    st.session_state.session_manager = session_manager
    # session_manager.refresh(model=model)

# Accept user input
for message in session_manager.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def play_voice(voice: Voice):
    from pydub import AudioSegment
    first_voice_latency = time.time() - stt
    for idx, chunk in enumerate(voice.byte_stream):
        encoded_audio = base64.b64encode(chunk).decode()

        # HTML + JavaScript 控制音频播放且隐藏控件
        audio_html = f"""
        <audio id="hidden_audio_{idx}" controls style="display:none;">
            <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">
        </audio>
        <script>
        var audio = document.getElementById('hidden_audio_{idx}');
        audio.play();
        </script>
        """
        st.components.v1.html(audio_html, height=0)
        duration = len(AudioSegment.from_file(io.BytesIO(chunk), format="mp3"))/1000
        # duration = 1
        logger.debug(f"play audio chunk with size:{len(chunk)}, duration:{duration}")
        time.sleep(duration-0.2)

    video_duration = get_duration(voice.file_path)

    st.audio(voice.file_path, format='audio/mp3', autoplay=False)
    msg = f"返回音频延时[{first_voice_latency:2.3f}]s, 音频时长[{video_duration:2.1f}]s"
    st.info(msg)


if prompt := st.chat_input("你好，你是谁？"):
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

    stt = time.time()
    resp = session_manager.get_resp(prompt)

    for token in resp:
        fist_token_latency = time.time() - stt
        full_response += token
        # st.info(full_response)
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    full_token_latency = time.time() - stt
    msg = f"返回[{len(full_response)}]字, 首字延时[{fist_token_latency: 2.3f}]s, 回复完成延时[{full_token_latency:2.3f}]s"
    st.info(msg)

    if speak:
        voice_config = dict(voice_id=voice_id, speed=speed, pitch=pitch)
        voice = session_manager.message2voice(full_response, voice_config=voice_config)
        play_voice(voice)

    user_message = {"role": "user", "content": prompt, "session_id": session_manager.session_id}
    assistant_message = {"role": "assistant", "content": full_response, "session_id": session_manager.session_id, "voice_path": voice.file_path}

    session_manager.add_message(user_message)
    session_manager.add_message(assistant_message)

    session_manager.round += 1
