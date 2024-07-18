#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/15 18:21:56
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''
import os
import sqlite3
from typing import List

from aifori.config import DB_DIR
from loguru import logger

from aifori.core import Message


def _get_connection():
    db_file = os.path.join(DB_DIR, "aifori.db")
    if not os.path.exists(db_file):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
    return sqlite3.connect(db_file)


def do_query(sql: str) -> List[dict] | dict:
    try:
        con = _get_connection()
        cur = con.cursor()
        logger.debug(f"query with {sql=}")
        cur.execute(sql)
        items = cur.fetchall()
        return items
    except Exception as e:
        logger.exception(e)
        raise e


def do_execute(sql: str):
    try:
        con = _get_connection()
        cur = con.cursor()
        logger.debug(f"execute with {sql=}")
        cur.execute(sql)
        con.commit()
    except Exception as e:
        logger.exception(e)
        raise e


def add_message(message: Message):
    sql = f"""insert into MESSAGE(ID,AGENT_ID,USER_ID,CONTENT) values ('{message.id}','{message.agent_id}','{message.user_id}','{message.content}')"""


def init_db():
    agent_sql = """
CREATE TABLE IF NOT EXISTS JOB(
    ID varchar PRIMARY KEY,
    STATUS TEXT NOT NULL,
    VOICE_CONFIG TEXT NOT NULL,
    CREATE_TIME TIMESTAMP DEFAULT (datetime('now','localtime')),
    UPDATE_TIME TIMESTAMP DEFAULT (datetime('now','localtime'))
)
    """
    message_sql = """
CREATE TABLE IF NOT EXISTS MESSAGE(
    ID varchar PRIMARY KEY,
    AGENT_ID TEXT NOT NULL,
    USER_ID TEXT NOT NULL,
    CONTENT TEXT NOT NULL,
    CREATE_TIME TIMESTAMP DEFAULT (datetime('now','localtime')),
    UPDATE_TIME TIMESTAMP DEFAULT (datetime('now','localtime'))
)
    """

    do_execute(agent_sql)
    do_execute(message_sql)


if __name__ == "__main__":
    init_db()
