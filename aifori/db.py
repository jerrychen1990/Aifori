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


def do_query(sql: str) -> List[dict] | dict:
    try:
        db_file = os.path.join(DB_DIR, "aifori.db")
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        logger.debug(f"updating job with sql:{sql}")
        cur.execute(sql)
        items = cur.fetchall()
        return items
    except Exception as e:
        logger.exception(e)
        raise e
