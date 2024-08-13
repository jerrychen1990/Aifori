#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/16 20:05:53
@Author  :   ChenHao
@Description  :  测试接口
@Contact :   jerrychen1990@gmail.com
'''

import glob
import os
import click
from loguru import logger
from aifori.config import DATA_DIR, DEFAULT_AI_DESC, DEFAULT_AI_NAME, DEFAULT_MODEL, DEFAULT_USER_DESC, DEFAULT_USER_NAME
from aifori.core import ChatRequest, ChatSpeakRequest, LLMGenConfig, SpeakRequest
from aifori.util import show_message
from snippets import set_logger
from aifori.client import AiForiClient
from snippets import load

set_logger("dev", __name__)

HOST = "http://localhost:9100"
ASSISTANT_ID = "test_service_assistant"
USER_ID = "test_service_user"
SESSION_ID = "test_service_session"
DO_SPEAK = False
MAX_TOKENS = 16


name = DEFAULT_AI_NAME
desc = DEFAULT_AI_DESC
model = DEFAULT_MODEL

user_name = DEFAULT_USER_NAME
user_desc = DEFAULT_USER_DESC

llm_gen_config = LLMGenConfig(max_tokens=MAX_TOKENS)

client = AiForiClient(host=HOST)
user_voice_config = dict(voice_id="junlang_nanyou", speed=1.4, pitch=-4)
voice_path = "./test_service_voice.mp3"


def set_up():
    resp = client.check_health()

    # create users
    assistant = client.create_assistant(assistant_id=ASSISTANT_ID, name=name, desc=desc, model=model)
    logger.info(f"{assistant=}")

    user = client.create_user(user_id=USER_ID, name=user_name, desc=user_desc)
    logger.info(f"{user=}")

    # clear session
    resp = client.clear_session(session_id=SESSION_ID)
    logger.info(resp)


def test_assistant():

    # round1
    client.clear_session(session_id=SESSION_ID)

    user_message = "你好,你叫什么名字?"
    # 批式回答
    req = ChatRequest(assistant_id=ASSISTANT_ID, user_id=USER_ID, message=user_message,
                      session_id=SESSION_ID, do_remember=True, llm_gen_config=llm_gen_config)
    assistant_message = client.chat(chat_request=req, stream=False)
    message = show_message(assistant_message)
    # logger.info(f"{assistant_message.content=}")
    assert "aifori" in assistant_message.content.lower()
    if DO_SPEAK:
        voice_path = "./tmp/test_service_voice1.mp3"
        speak_req = SpeakRequest(assistant_id=ASSISTANT_ID, message=message, save_voice=False, voice_path=voice_path)
        client.speak(speak_req, play=True, local_voice_path=voice_path)

    # round2
    user_message = "你知道我叫什么吗"
    req = ChatRequest(assistant_id=ASSISTANT_ID, user_id=USER_ID, message=user_message,
                      session_id=SESSION_ID, do_remember=True, llm_gen_config=llm_gen_config)

    assistant_message = client.chat(chat_request=req, stream=True)
    message = show_message(assistant_message)
    if DO_SPEAK:
        voice_path = "./tmp/test_service_voice2.mp3"
        speak_req = SpeakRequest(assistant_id=ASSISTANT_ID, message=message, save_voice=False, voice_path=voice_path)
        client.speak(speak_req, play=True, local_voice_path=voice_path)

    # round3
    user_message = "列出三位诗人"
    # client.speak(assistant_id=AGENT_ID, message=user_message, voice_config=user_voice_config)
    # 流式回答
    req = ChatRequest(assistant_id=ASSISTANT_ID, user_id=USER_ID, message=user_message,
                      session_id=SESSION_ID, do_remember=True, llm_gen_config=llm_gen_config)
    assistant_message = client.chat(chat_request=req, stream=True)
    message = show_message(assistant_message)
    if DO_SPEAK:
        voice_path = "./tmp/test_service_voice3.mp3"
        speak_req = SpeakRequest(assistant_id=ASSISTANT_ID, message=message, save_voice=True, voice_path=voice_path)
        client.speak(speak_req, play=True, local_voice_path=voice_path)

    # round4
    user_message = "第二位是哪个朝代的"
    # client.speak(assistant_id=AGENT_ID, message=user_message, voice_config=user_voice_config)
    # 回答+朗读
    voice_path = "./tmp/test_service_voice4.mp3"
    chat_speak_request = ChatSpeakRequest(assistant_id=ASSISTANT_ID, user_id=USER_ID, session_id=SESSION_ID, do_remember=True, return_voice=True, return_text=True,
                                          voice_config=user_voice_config, message=user_message, voice_path=voice_path, llm_gen_config=llm_gen_config)
    assistant_message, voice = client.chat_speak_stream(chat_speak_request=chat_speak_request, local_voice_path=voice_path, play=DO_SPEAK)
    message = show_message(assistant_message)


def clear_tmp_voices():

    # 指定目标目录和文件匹配模式
    directory = './tmp'
    pattern = 'test_service_*.mp3'  # 匹配所有以 .log 结尾的文件
    # 获取符合模式的文件列表
    files_to_delete = glob.glob(os.path.join(directory, pattern))

    # 删除匹配的文件
    for file_path in files_to_delete:
        os.remove(file_path)
        logger.info(f"Deleted: {file_path}")


def clean_up():
    client.delete_assistant(assistant_id=ASSISTANT_ID)
    client.delete_user(user_id=USER_ID)
    client.clear_session(session_id=SESSION_ID)
    clear_tmp_voices()


def test_rule():
    client.update_rule(rule_path=os.path.join(DATA_DIR, "rule/rule_old.jsonl"))
    # round1
    user_message = "你好呀,你叫什么名字"
    req = ChatRequest(assistant_id=ASSISTANT_ID, user_id=USER_ID, message=user_message,
                      session_id=SESSION_ID, do_remember=False, llm_gen_config=llm_gen_config)
    assistant_message = client.chat(req, stream=False)
    message = show_message(assistant_message)
    assert "你好呀，我叫Aifori，很高兴认识你！" == message

    client.update_rule(rule_path=os.path.join(DATA_DIR, "rule/rule_new.jsonl"))
    user_message = "我叫神尼名字"
    req = ChatRequest(assistant_id=ASSISTANT_ID, user_id=USER_ID, message=user_message,
                      session_id=SESSION_ID, do_remember=False, llm_gen_config=llm_gen_config)
    assistant_message = client.chat(req, stream=True)
    message = show_message(assistant_message)
    logger.info(f"{message=}")
    assert "你叫Nobody" == message

    # client.update_rule(rule_path=os.path.join(DATA_DIR, "rule/rule_new.jsonl"))


def test_session():
    messages = client.list_messages(assistant_id=ASSISTANT_ID, session_id=SESSION_ID, limit=20)
    logger.info(f"{messages=}")
    assert len(messages) == 8, f"session messages should be 8, but got {len(messages)}"


@click.command()
@click.argument('config_path')
def main(config_path: str):
    config = load(config_path)
    globals().update(**config)
    logger.info(f"testing with config:{config}")
    # logger.info(f"{DO_SPEAK=}")
    # logger.info(globals())

    try:
        set_up()
        test_rule()
        test_assistant()
        test_session()
        clean_up()
        logger.info("☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺TEST SUCCESS☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺")

    except Exception as e:
        logger.error("test service failed!")
        clean_up()
        logger.exception(e)


if __name__ == "__main__":
    main()
