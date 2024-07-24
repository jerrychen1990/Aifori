#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/24 16:49:57
@Author  :   ChenHao
@Description  :   规则相关
@Contact :   jerrychen1990@gmail.com
'''

import os
import re
from typing import List

from aifori.config import DEFAULT_RULE_NAME, RULE_DIR
from snippets import load_with_cache
from loguru import logger


def rule_match(query: str, rule_file_name: str = DEFAULT_RULE_NAME, regex=False, match_all=True) -> List[dict]:
    file_path = os.path.join(RULE_DIR, rule_file_name)
    rules = load_with_cache(file_path)
    logger.debug(f"check {len(rules)} rules for query: {query}")
    rs = []

    for rule in rules:
        key = rule["key"]
        if isinstance(key, list):
            if any(k in query for k in key):
                rs.append(rule)
                if not match_all:
                    break
        else:
            if not regex:
                if isinstance(key, str) and key in query:
                    rs.append(rule)
                    if not match_all:
                        break
            else:
                if re.search(key, query):
                    rs.append(rule)
                    if not match_all:
                        break

    return rs
