#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/16 20:05:53
@Author  :   ChenHao
@Description  :  测试接口
@Contact :   jerrychen1990@gmail.com
'''

from loguru import logger
from aifori.tts import play_voice
from snippets import set_logger
from aifori.client import AiForiClient


set_logger("dev", __name__)

HOST = "http://localhost:9001"
AGENT_ID = "test_service_agent"
USER_ID = "test_service_user"
SESSION_ID = "test_service_session"
name = "Aifori"
desc = "你拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话"
model = "glm-4-air"


client = AiForiClient(host=HOST)
user_voice_config = dict(voice_id="junlang_nanyou")


def test_agent():
    agent = client.create_agent(agent_id=AGENT_ID, name=name, desc=desc, model=model)
    logger.info(agent)

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
    client.speak(agent_id=AGENT_ID, message=content, max_word=50)

    # round3
    user_message = "第二位是哪个朝代的"
    # client.speak(agent_id=AGENT_ID, message=user_message, tts_config=user_voice_config)
    # 回答+朗读
    assistant_message, voice = client.chat_and_speak(agent_id=AGENT_ID, user_id=USER_ID, session_id=SESSION_ID, message=user_message, max_word=50)
    logger.info(f"{assistant_message.content=}")
    play_voice(voice)


if __name__ == "__main__":
    try:
        client.check_health()
        test_agent()
        client.delete_agent(agent_id=AGENT_ID)
        logger.info("☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺TEST SUCCESS☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺")

    except Exception as e:
        logger.error("test_service.py failed")
        client.delete_agent(agent_id=AGENT_ID)
        logger.exception(e)