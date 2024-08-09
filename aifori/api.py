#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 17:47:34
@Author  :   ChenHao
@Description  :   api层
@Contact :   jerrychen1990@gmail.com
'''
from threading import Thread
from typing import Iterable
from aifori.agent import AIAgent, Human
from aifori.buffer import Buffer
from aifori.config import *
from aifori.core import AgentMessage, Session, StreamAgentMessage, UserMessage, Voice
from aifori.session import SESSION_MANAGER
from snippets import load


def get_session(session_id: str) -> Session:
    file_path = os.path.join(SESSION_DIR, session_id+".json")
    session_config = load(file_path)
    session = Session.model_validate(session_config)
    return session

def clear_session(session_id: str):
    logger.info(f"clear session {session_id}")
    SESSION_MANAGER.clear_session(session_id)



def get_agent(agent_id: str) -> AIAgent:
    agent = AIAgent.from_config(id=agent_id)
    return agent


def get_user(user_id: str) -> Human:
    user = Human.from_config(id=user_id)
    return user


def create_agent(name: str, desc: str, id: str, model: str, voice_config: dict = DEFAULT_VOICE_CONFIG, exists_ok=True, do_save=True) -> AIAgent:
    try:
        agent = get_agent(id)
        msg = f"agent:{id} already exists, will not create new one"
        logger.warning(msg)
        if not exists_ok:
            raise Exception(msg)
        else:
            return agent
    except Exception as e:
        pass

    agent = AIAgent(name=name, desc=desc, model=model, id=id, voice_config=voice_config)
    if do_save:
        agent.save()
    return agent


def create_user(name: str, desc: str, id: str, exists_ok=True, do_save=True) -> Human:
    try:
        user = get_user(id)
        msg = f"user:{id} already exists, will not create new one"
        logger.warning(msg)
        if not exists_ok:
            raise Exception(msg)
        else:
            return user
    except Exception as e:
        pass

    user = Human(name=name, desc=desc, id=id)
    if do_save:
        user.save()
    return user


def delete_agent(agent_id: str):
    config_path = os.path.join(AGENT_DIR, agent_id+".json")
    if os.path.exists(config_path):
        logger.info(f"Delete agent config file: {config_path}")
        os.remove(config_path)


def delete_user(user_id: str):
    config_path = os.path.join(AGENT_DIR, user_id+".json")
    if os.path.exists(config_path):
        logger.info(f"Delete agent config file: {config_path}")
        os.remove(config_path)


def speak_agent_stream(agent_id: str, message: str, voice_config: dict, chunk_size: int = 1024 * 10) -> Voice:
    logger.info(f"agent {agent_id} speak {message} with {voice_config=}")
    agent = get_agent(agent_id)
    if not agent:
        raise Exception(f"agent:{agent_id} not found")
    voice: Voice = agent.speak(message=message, stream=True, **voice_config)

    def chunk_stream(stream):
        acc = b""
        for chunk in stream:
            acc += chunk
            if len(acc) >= chunk_size:
                yield acc[:chunk_size]
                acc = acc[chunk_size:]
        if acc:
            yield acc

    voice.byte_stream = chunk_stream(voice.byte_stream)
    return voice


def chat_agent_stream(agent_id: str,
                      user_id: str,
                      session_id: str,
                      message: str,
                      do_remember: bool = False,
                      recall_memory: bool = False,
                      return_text: bool = True,
                      text_chunk_size: int = DEFAULT_TEXT_CHUNK_SIZE,
                      voice_config: dict = DEFAULT_VOICE_CONFIG,
                      return_voice: bool = False,
                      voice_chunk_size: int = DEFAULT_VOICE_CHUNK_SIZE) -> Iterable[dict]:
    agent = get_agent(agent_id)
    user_message = UserMessage(content=message, user_id=user_id)
    buffer = Buffer()

    def _chat(buffer: Buffer):
        agent_message: StreamAgentMessage = agent.chat(
            message=user_message,  stream=True, session_id=session_id, recall_memory=recall_memory, temperature=0)
        if do_remember:
            SESSION_MANAGER.add_message(user_message, to_id=agent_id, to_role="agent", session_id=session_id)
        for chunk in agent_message.content:
            buffer.add_text(chunk)
        message = AgentMessage(content=buffer.text, user_id=agent_id)
        logger.info(f"agent {agent_id} reply {message} for user message:{user_message}")
        if do_remember:
            SESSION_MANAGER.add_message(message, to_id=user_id, to_role="user", session_id=session_id)
        buffer.text_done = True

    def _speak(buffer: Buffer):
        for text_chunk in buffer.gen_tts(text_chunk_size=text_chunk_size):
            # voice = speak_agent_stream(agent_id, buffer.text, voice_config, chunk_size=voice_chunk_size)
            logger.debug(f"speak {text_chunk}")
            # print(f"speak {text_chunk}")

            voice: Voice = agent.speak(message=text_chunk["text_chunk"], stream=True, **voice_config)
            for chunk in voice.byte_stream:
                logger.debug(f"add voice chunk {len(chunk)}, {type(chunk)=}, {chunk[:4]=} to buffer")
                # print(f"add voice chunk {len(chunk)}, {type(chunk)=}, {chunk[:4]=} to buffer")

                buffer.add_voice(chunk)

        buffer.voice_done = True

    chat_thread = Thread(target=_chat, args=(buffer,))
    chat_thread.start()

    if return_voice:
        speak_thread = Thread(target=_speak, args=(buffer,))
        logger.debug("speak_thread start")
        # print("speak start")
        speak_thread.start()

    return buffer.gen(gen_text=return_text, text_chunk_size=text_chunk_size, gen_voice=return_voice, voice_chunk_size=voice_chunk_size)
