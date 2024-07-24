#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/08 17:47:34
@Author  :   ChenHao
@Description  :   api层
@Contact :   jerrychen1990@gmail.com
'''
from aifori.agent import AIAgent, HumanAgent
from aifori.config import *
from aifori.core import Session
from snippets import load


def get_session(session_id: str) -> Session:
    file_path = os.path.join(SESSION_DIR, session_id+".json")
    session_config = load(file_path)
    session = Session.model_validate(session_config)
    return session


def get_assistant(assistant_id: str) -> AIAgent:
    assistant = AIAgent.from_config(id=assistant_id)
    return assistant


def get_user(user_id: str) -> HumanAgent:
    user = HumanAgent.from_config(id=user_id)
    return user


def create_assistant(name: str, desc: str, id: str, model: str, voice_config: dict = DEFAULT_VOICE_CONFIG, exists_ok=True, do_save=True) -> AIAgent:
    try:
        assistant = get_assistant(id)
        msg = f"agent:{id} already exists, will not create new one"
        logger.warning(msg)
        if not exists_ok:
            raise Exception(msg)
        else:
            return assistant
    except Exception as e:
        pass

    assistant = AIAgent(name=name, desc=desc, model=model, id=id, voice_config=voice_config)
    if do_save:
        assistant.save()
    return assistant


def create_user(name: str, desc: str, id: str, exists_ok=True, do_save=True) -> HumanAgent:
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

    user = HumanAgent(name=name, desc=desc, id=id)
    if do_save:
        user.save()
    return user


def delete_assistant(assistant_id: str):
    config_path = os.path.join(AGENT_DIR, assistant_id+".json")
    if os.path.exists(config_path):
        logger.info(f"Delete assistant config file: {config_path}")
        os.remove(config_path)


def delete_user(user_id: str):
    config_path = os.path.join(AGENT_DIR, user_id+".json")
    if os.path.exists(config_path):
        logger.info(f"Delete assistant config file: {config_path}")
        os.remove(config_path)
