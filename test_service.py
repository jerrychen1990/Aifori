#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/16 20:05:53
@Author  :   ChenHao
@Description  :  测试接口
@Contact :   jerrychen1990@gmail.com
'''

import os
import click
from loguru import logger
from aifori.config import DATA_DIR, DEFAULT_AI_DESC, DEFAULT_AI_NAME, DEFAULT_MODEL, DEFAULT_USER_DESC, DEFAULT_USER_NAME
from aifori.tts import play_voice
from aifori.util import show_stream_content
from snippets import set_logger
from aifori.client import AiForiClient
from snippets import load

set_logger("dev", __name__)

HOST = "http://localhost:9001"
AGENT_ID = "test_service_agent"
USER_ID = "test_service_user"
SESSION_ID = "test_service_session"
DO_SPEAK = False


name = DEFAULT_AI_NAME
desc = DEFAULT_AI_DESC
model = DEFAULT_MODEL

user_name = DEFAULT_USER_NAME
user_desc = DEFAULT_USER_DESC

client = AiForiClient(host=HOST)
user_voice_config = dict(voice_id="junlang_nanyou", speed=1.4, pitch=-4)
voice_path = "./test_service_voice.mp3"


def set_up():
    resp = client.check_health()

    # create users
    agent = client.create_agent(agent_id=AGENT_ID, name=name, desc=desc, model=model)
    logger.info(f"{agent=}")

    user = client.create_user(user_id=USER_ID, name=user_name, desc=user_desc)
    logger.info(f"{user=}")

    # clear session
    resp = client.clear_session(session_id=SESSION_ID)
    logger.info(resp)


def test_agent():

    # round1
    user_message = "你好,你叫什么名字?"
    # client.speak(agent_id=AGENT_ID, message=user_message, voice_config=user_voice_config)
    # 批式回答
    assistant_message = client.chat(agent_id=AGENT_ID, user_id=USER_ID, message=user_message, session_id=SESSION_ID, stream=False, do_remember=True)
    logger.info(f"{assistant_message.content=}")
    assert "aifori" in assistant_message.content.lower()
    if DO_SPEAK:
        client.speak(agent_id=AGENT_ID, message=assistant_message.content, max_word=50)

    # round2
    user_message = "你知道我叫什么吗"
    assistant_message = client.chat(agent_id=AGENT_ID, user_id=USER_ID, message=user_message, session_id=SESSION_ID, stream=False, do_remember=True)
    logger.info(f"{assistant_message.content=}")
    if DO_SPEAK:
        client.speak(agent_id=AGENT_ID, message=assistant_message.content, max_word=50, voice_config=user_voice_config)

    # round3
    user_message = "列出三位诗人"
    # client.speak(agent_id=AGENT_ID, message=user_message, voice_config=user_voice_config)
    # 流式回答
    assistant_message = client.chat(agent_id=AGENT_ID, user_id=USER_ID, message=user_message, session_id=SESSION_ID, stream=True, do_remember=True)
    content = show_stream_content(assistant_message.content)
    if DO_SPEAK:
        client.speak(agent_id=AGENT_ID, message=content, max_word=50)

    # round4
    user_message = "第二位是哪个朝代的"
    # client.speak(agent_id=AGENT_ID, message=user_message, voice_config=user_voice_config)
    # 回答+朗读
    assistant_message, voice = client.chat_and_speak(agent_id=AGENT_ID, user_id=USER_ID, session_id=SESSION_ID, voice_config=user_voice_config,
                                                     dump_path=voice_path, play_local=False, message=user_message, max_word=50)

    logger.info(f"{assistant_message.content=}")
    play_voice(voice_path)


def clean_up():
    client.delete_agent(agent_id=AGENT_ID)
    client.delete_user(user_id=USER_ID)
    client.clear_session(session_id=SESSION_ID)


def test_rule():
    client.update_rule(rule_path=os.path.join(DATA_DIR, "rule/rule_old.jsonl"))
    # round1
    user_message = "你好呀,你叫什么名字"
    assistant_message = client.chat(agent_id=AGENT_ID, user_id=USER_ID, message=user_message, session_id=SESSION_ID, stream=False, do_remember=False)
    logger.info(f"{assistant_message.content=}")
    assert "你好呀，我叫Aifori，很高兴认识你！" == assistant_message.content

    client.update_rule(rule_path=os.path.join(DATA_DIR, "rule/rule_new.jsonl"))
    user_message = "我叫神尼名字"
    assistant_message = client.chat(agent_id=AGENT_ID, user_id=USER_ID, message=user_message, session_id=SESSION_ID, stream=True, do_remember=False)
    content = show_stream_content(assistant_message.content)
    logger.info(f"{content=}")
    assert "你叫Nobody" == content

    # client.update_rule(rule_path=os.path.join(DATA_DIR, "rule/rule_new.jsonl"))


def test_session():
    messages = client.list_messages(agent_id=AGENT_ID, session_id=SESSION_ID, limit=20)
    logger.info(f"{messages=}")
    assert len(messages) == 8, f"session messages should be 6, but got {len(messages)}"


@click.command()
@click.argument('config_path')
def main(config_path: str):
    config = load(config_path)
    globals().update(**config)
    logger.info(f"testing with config:{config}")
    # logger.info(f"{DO_SPEAK=}")
    logger.info(globals())

    try:
        set_up()
        test_rule()
        test_agent()
        test_session()
        clean_up()
        logger.info("☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺TEST SUCCESS☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺")

    except Exception as e:
        logger.error("test service failed!")
        clean_up()
        logger.exception(e)


if __name__ == "__main__":
    main()
