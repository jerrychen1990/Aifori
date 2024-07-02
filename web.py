#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/02 17:24:15
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import streamlit as st

from agent import *


models = ["emohaa"]
model = st.sidebar.selectbox("模型", models)
clear = st.sidebar.button("清空历史")


def get_resp(prompt):
    history = st.session_state.messages
    user_info = AgentInfo(name="张三", desc="30岁的男性软件工程师，兴趣包括阅读、徒步和编程")
    agent_info = AgentInfo(name="Emohaa", desc="Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话")
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
    st.session_state.messages.append(
        {"role": "user", "content": prompt})
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})
