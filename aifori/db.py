#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/15 18:21:56
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''
import datetime
import json
import os
import sqlite3
from typing import List


from aifori.config import DB_DIR
from loguru import logger

from sqlalchemy import DateTime, create_engine, Column, Integer, String

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from aifori.core import Message


# SQLAlchemy ORM 基础类
Base = declarative_base()

# 定义 SQLAlchemy ORM 模型


class MessageORM(Base):
    __tablename__ = 'Message'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    content = Column(String)
    from_role = Column(String, index=True)
    to_role = Column(String, index=True)
    from_id = Column(String, index=True)
    to_id = Column(String, index=True)
    tool_calls = Column(String)
    create_datetime = Column(DateTime, default=datetime.datetime.now())

    @classmethod
    def from_message(cls, message: Message, to_id: str, to_role: str):
        orm_message = cls(content=message.content, from_id=message.user_id, to_id=to_id, from_role=message.role, to_role=to_role)
        return orm_message

    def to_message(self) -> Message:
        return Message(content=self.content, role=self.from_role,  user_id=self.from_id)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "from_role": self.from_role,
            "from_id": self.from_id,
            "content": self.content,
            "to_role": self.to_role,
            "to_id": self.to_id,
            "create_datetime": self.create_datetime
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)


def get_db_session():
    db_file = os.path.join(DB_DIR, "aifori.db")
    if not os.path.exists(db_file):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)

    engine = create_engine(f'sqlite:///{db_file}')

    Base.metadata.create_all(bind=engine)

    # 创建数据库会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db


DB = get_db_session()


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


# def add_message(message: Message):
#     sql = f"""insert into MESSAGE(ID,AGENT_ID,USER_ID,CONTENT) values ('{message.user_id}','{message.agent_id}','{message.user_id}','{message.content}')"""


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
    pass
    # init_db()
    # add_message(AssistantMessage(user_id="123",  content="789"))
