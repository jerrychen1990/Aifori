#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/16 20:05:53
@Author  :   ChenHao
@Description  :  测试接口
@Contact :   jerrychen1990@gmail.com
'''

import click
from loguru import logger
from aifori.tts import dump_voice
from snippets import set_logger
from aifori.client import AiForiClient
from snippets import load

set_logger("dev", __name__)

HOST = "http://localhost:9001"
AGENT_ID = "test_service_agent"
USER_ID = "test_service_user"
SESSION_ID = "test_service_session"
DO_SPEAK = False


name = "Aifori"
desc = "你是一名专业的心理咨询师"
model = "glm-4"

user_name = "NoBody"
user_desc = "一个空巢年轻人,没有朋友,没有爱人,没有工作,没有希望。喜欢音乐和诗歌，喜欢一切华美而哀伤的事物。"


client = AiForiClient(host=HOST)
user_voice_config = dict(voice_id="junlang_nanyou")
voice_path = "./test_service_voice.mp3"


def test_agent():
    # create users
    agent = client.create_agent(agent_id=AGENT_ID, name=name, desc=desc, model=model)
    logger.info(f"{agent=}")

    user = client.create_user(user_id=USER_ID, name=user_name, desc=user_desc)
    logger.info(f"{user=}")

    # clear session
    resp = client.clear_session(session_id=SESSION_ID)
    logger.info(resp)

    # round1
    user_message = "你好,你叫什么名字?"
    # client.speak(agent_id=AGENT_ID, message=user_message, tts_config=user_voice_config)
    # 批式回答
    assistant_message = client.chat(agent_id=AGENT_ID, user_id=USER_ID, message=user_message, session_id=SESSION_ID, stream=False, do_remember=True)
    logger.info(f"{assistant_message.content=}")
    assert "aifori" in assistant_message.content.lower()
    if DO_SPEAK:
        client.speak(agent_id=AGENT_ID, message=assistant_message.content, max_word=50)

    user_message = "你知道我叫什么吗"
    assistant_message = client.chat(agent_id=AGENT_ID, user_id=USER_ID, message=user_message, session_id=SESSION_ID, stream=False, do_remember=True)
    logger.info(f"{assistant_message.content=}")
    if DO_SPEAK:
        client.speak(agent_id=AGENT_ID, message=assistant_message.content, max_word=50)

    # round2
    user_message = "列出三位诗人"
    # client.speak(agent_id=AGENT_ID, message=user_message, tts_config=user_voice_config)
    # 流式回答
    assistant_message = client.chat(agent_id=AGENT_ID, user_id=USER_ID, message=user_message, session_id=SESSION_ID, stream=True, do_remember=True)
    content = ""
    tmp_chunk = ""
    for chunk in assistant_message.content:
        tmp_chunk += chunk
        if len(tmp_chunk) > 10:
            logger.info(f"{tmp_chunk=}")
            content += tmp_chunk
            tmp_chunk = ""
    content += tmp_chunk
    logger.info(f"{content=}")
    if DO_SPEAK:
        client.speak(agent_id=AGENT_ID, message=content, max_word=50)

    # round3
    user_message = "第二位是哪个朝代的"
    # client.speak(agent_id=AGENT_ID, message=user_message, tts_config=user_voice_config)
    # 回答+朗读
    speak_callbacks = [[dump_voice, dict(path=voice_path)]]
    if DO_SPEAK:
        speak_callbacks.append()
    assistant_message, voice = client.chat_and_speak(agent_id=AGENT_ID, user_id=USER_ID, session_id=SESSION_ID,
                                                     speak_callbacks=speak_callbacks, message=user_message, max_word=50)
    logger.info(f"{assistant_message.content=}")


def clean_up():
    client.delete_agent(agent_id=AGENT_ID)
    client.delete_user(user_id=USER_ID)


@click.command()
@click.argument('config_path')
def main(config_path: str):
    config = load(config_path)
    locals().update(**config)
    logger.info(f"testing with config:{config}")
    logger.info(locals())
    try:
        client.check_health()
        test_agent()
        clean_up()
        logger.info("☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺TEST SUCCESS☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺")

    except Exception as e:
        logger.error("test service failed!")
        clean_up()
        logger.exception(e)


if __name__ == "__main__":
    main()
