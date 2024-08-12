#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 17:47:34
@Author  :   ChenHao
@Description  :   api层
@Contact :   jerrychen1990@gmail.com
'''
import itertools
from threading import Thread
from typing import Iterable, List, Tuple


from aifori.agent import AIAgent, Human
from aifori.buffer import Buffer
from aifori.config import *
from aifori.core import AssistantMessage, ChatRequest, ChatSpeakRequest, SpeakRequest, StreamAssistantMessage, UserMessage, Voice
from aifori.session import SESSION_MANAGER
from liteai.voice import build_voice, dump_voice_stream
from snippets.utils import add_callback2gen


def clear_session(session_id: str):
    logger.info(f"clear session {session_id}")
    SESSION_MANAGER.clear_session(session_id)


def get_assistant(id: str) -> AIAgent:
    agent = AIAgent.from_config(id=id)
    return agent


def get_user(id: str) -> Human:
    user = Human.from_config(id=id)
    return user


def create_assistant(name: str, desc: str, id: str, model: str, voice_config: dict = DEFAULT_VOICE_CONFIG, exists_ok=True, do_save=True) -> AIAgent:
    try:
        agent = get_assistant(id)
        msg = f"assistant:{id} already exists, will not create new one"
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


def delete_assistant(id: str):
    return AIAgent.delete(id)


def delete_user(id: str):
    return Human.delete(id)


def chat_assistant(chat_request: ChatRequest, stream=True, **kwargs) -> AssistantMessage | StreamAssistantMessage:
    assistant = get_assistant(chat_request.assistant_id)
    user = get_user(chat_request.user_id)
    user_message = UserMessage(content=chat_request.message, user_id=user.id)
    session_id = chat_request.session_id
    assistant_message = assistant.chat(
        message=user_message,  stream=stream, session_id=session_id, recall_memory=chat_request.recall_memory,
        **chat_request.llm_gen_config.model_dump(), **kwargs)
    do_remember = chat_request.do_remember
    if do_remember:
        SESSION_MANAGER.add_message(user_message, to_id=assistant.id, to_role="agent", session_id=session_id)
        if stream:
            def _remember_callback(chunks: List[str], **kwargs):
                message = AssistantMessage(content="".join(chunks), user_id=assistant.id)
                SESSION_MANAGER.add_message(message, to_id=user.id, to_role="user", session_id=session_id)
            assistant_message.content = add_callback2gen(assistant_message.content, _remember_callback)
        else:
            SESSION_MANAGER.add_message(assistant_message, to_id=user.id, to_role="user", session_id=session_id)
    return assistant_message


def speak_assistant(speak_request: SpeakRequest, stream=True) -> Voice:
    assistant = get_assistant(speak_request.assistant_id)
    voice: Voice = assistant.speak(message=speak_request.message, stream=stream, voice_path=speak_request.voice_path,  **speak_request.voice_config)
    chunk_size = speak_request.voice_chunk_size

    def _chunk_stream(stream):
        acc = b""
        for chunk in stream:
            acc += chunk
            if len(acc) >= chunk_size:
                yield acc[:chunk_size]
                acc = acc[chunk_size:]
        if acc:
            yield acc
    voice.byte_stream = _chunk_stream(voice.byte_stream)
    return voice


def chat_speak_assistant(req: ChatSpeakRequest) -> Iterable[dict]:
    assistant = get_assistant(req.assistant_id)
    assistant_id = assistant.id
    user_message = UserMessage(content=req.message, user_id=req.user_id)
    session_id = req.session_id
    buffer = Buffer()

    def _chat(buffer: Buffer):
        agent_message: StreamAssistantMessage = assistant.chat(
            message=user_message,  stream=True, session_id=session_id, recall_memory=req.recall_memory, **req.llm_gen_config.model_dump())
        if req.do_remember:
            SESSION_MANAGER.add_message(user_message, to_id=assistant_id, to_role="agent", session_id=session_id)
        for chunk in agent_message.content:
            buffer.add_text(chunk)
        message = AssistantMessage(content=buffer.text, user_id=assistant_id)
        logger.info(f"agent {assistant_id} reply {message} for user message:{user_message}")
        if req.do_remember:
            SESSION_MANAGER.add_message(message, to_id=req.user_id, to_role="user", session_id=session_id)
        buffer.text_done = True

    def _speak(buffer: Buffer):
        for text_chunk in buffer.gen_tts(text_chunk_size=req.tts_text_chunk_size):
            logger.debug(f"speak: [{text_chunk}], with size {len(text_chunk)}")
            voice: Voice = assistant.speak(message=text_chunk, stream=True, **req.voice_config)
            for chunk in voice.byte_stream:
                buffer.add_voice(chunk)
        if req.voice_path:
            dump_voice_stream(buffer.voice_stream, req.voice_path)
        buffer.voice_done = True

    chat_thread = Thread(target=_chat, args=(buffer,))
    chat_thread.start()

    if req.return_voice:
        speak_thread = Thread(target=_speak, args=(buffer,))
        logger.debug("speak_thread start")
        # print("speak start")
        speak_thread.start()
    return buffer.gen(gen_text=req.return_text, text_chunk_size=req.text_chunk_size, gen_voice=req.return_voice, voice_chunk_size=req.voice_chunk_size)


def decode_chunks(chunks: Iterable[dict], assistant_id: str, return_voice: bool, local_file_path: str) -> Tuple[StreamAssistantMessage, Voice]:
    s1, s2 = itertools.tee(chunks)
    text_stream = (e["text_chunk"] for e in s1 if "text_chunk" in e)
    message = StreamAssistantMessage(user_id=assistant_id, content=text_stream)
    if return_voice:
        voice_stream = (e["voice_chunk"] for e in s2 if e.get("voice_chunk"))
        voice_stream = (eval(e) if isinstance(e, str) else e for e in voice_stream)

        voice = build_voice(byte_stream=voice_stream, file_path=local_file_path)
    else:
        voice = None
    return message, voice
