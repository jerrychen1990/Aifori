#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/09 17:11:48
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import os
import streamlit as st
from aifori.config import DATA_DIR
from snippets import load, dump
import datetime
import time
from loguru import logger

data_path = os.path.join(DATA_DIR, "adopters.jsonl")

recipient_email = "jerrychen1990@gmail.com"

# Streamlit 表单
st.title("Aifori Wishlist")
st.markdown("请填写您的愿望清单，我们会根据您的需求尽快开发😄")
with st.form(key='email_form'):
    sent_email = st.text_input("您的邮箱（我们功能上线之后会通过邮箱通知您，必填）")

    st.markdown("您会在那些场景下使用Aifori？")
    dairy = st.checkbox("写日记")
    mental = st.checkbox("心理疗愈")
    company = st.checkbox("日常陪伴")
    art = st.checkbox("音乐推荐")
    other = st.text_input("其他场景")

    message = st.text_area("想对我们说的话")
    # subject = st.text_input("主题")
    submit_button = st.form_submit_button(label='发送')

st.markdown("给创作者留言 [jerrychen1990@gmail.com](mailto:jerrychen1990@gmail.com)")


if submit_button:
    items = load(data_path) if os.path.exists(data_path) else []
    cur_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
    item = dict(cur_time=cur_time, sent_email=sent_email, dairy=dairy, mental=mental, company=company,
                art=art, other=other,  message=message)
    items.append(item)
    logger.info(f"Received new item: {item}")
    dump(items, data_path)
    st.info("感谢您的反馈，我们会尽快处理您的需求！")
