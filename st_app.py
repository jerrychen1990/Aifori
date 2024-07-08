#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/02 17:24:15
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import uuid
import streamlit as st

from aifori.agent import Agent, AgentInfo
from aifori.tts import tts
from aifori.config import *
from loguru import logger

# print(logger._core.handlers)


user_name = st.sidebar.text_input("用户名", DEFAULT_USER_NAME)
user_desc = st.sidebar.text_area("用户描述", DEFAULT_USER_DESC, height=100)

ai_name = st.sidebar.text_input("AI名称", DEFAULT_AI_NAME)
ai_desc = st.sidebar.text_area("用户描述", DEFAULT_AI_DESC, height=100)


model = st.sidebar.selectbox("模型", LLM_MODELS)
character = st.sidebar.selectbox("音色", CHARACTER_MAP.keys())
clear = st.sidebar.button("清空历史")
voice_id = CHARACTER_MAP[character]["voice_id"]
# desc = character_map[character]["desc"]
speed = st.sidebar.slider("语速", 0.5, 2.0, 1.0)
pitch = st.sidebar.slider("音调", -12, 12, 0, 1)


def get_resp(prompt):
    history = st.session_state.messages
    user_info = AgentInfo(name=user_name, desc=user_desc)
    agent_info = AgentInfo(name=ai_name, desc=ai_desc)
    agent = Agent(agent_info)
    messages = history+[{"role": "user", "content": prompt}]
    resp = agent.chat(user_info=user_info, messages=messages, model=model)
    return resp


if clear:
    st.info("历史已清空")
    st.session_state.messages = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# Accept user input
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id
idx = 0

if prompt := st.chat_input("你好，你是谁？"):
    # st.info(prompt)
    # Add user message to chat history
    # logger.info("add message")
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

    resp = get_resp(prompt)
    for token in resp:
        full_response += token
        # st.info(full_response)
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    tgt_path = os.path.join(VOICE_DIR, "minimax", f"{session_id}_{idx}.mp3")
    gen_voice = tts(full_response, provider="minimax", tgt_path=tgt_path, voice_id=voice_id, speed=speed, pitch=pitch, stream=False)
    # logger.info(f"{gen_voice=}")
    user_message = {"role": "user", "content": prompt, "session_id": session_id}
    assistant_message = {"role": "assistant", "content": full_response, "session_id": session_id, "gen_voice": gen_voice}

    logger.info(f"{user_message=}")
    logger.info(f"{assistant_message=}")
    st.audio(gen_voice, format='audio/mp3', autoplay=True)

    st.session_state.messages.append(
        user_message
    )
    st.session_state.messages.append(
        assistant_message)
    idx += 1
