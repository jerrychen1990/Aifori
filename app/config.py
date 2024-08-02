#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/22 19:44:49
@Author  :   ChenHao
@Description  :  aifori页面
@Contact :   jerrychen1990@gmail.com
'''


import os


LLM_MODELS = ["glm-4-airx",  "glm-4-0520", "glm-4-flash", "emohaa"]
HOST = "http://127.0.0.1:9001"


CHARACTER_MAP = {
    "甜心小玲": {
        "voice_id": "tianxin_xiaoling",
        "desc": "一个可爱、甜美、活泼的女生，声音甜美而治愈。"

    },
    "淡雅学姐": {
        "voice_id": "danya_xuejie",
        "desc": "一个优雅、知性、成熟的女性，声音温柔而坚定。"
    },
    "俊朗男友": {
        "voice_id": "junlang_nanyou",
        "desc": "一个阳光、帅气、充满自信的男生，声音温暖而磁性。"
    },
    "霸道少爷": {
        "voice_id": "badao_shaoye",
        "desc": "一个霸气、自信、帅气的男生，声音低沉而有力。"
    }
}

PROFILE_PATH = os.path.abspath(os.path.dirname(__file__)) + "/profile.json"

USER_AGENTS = {
    "Aifori-Nobody": {
        "agent_id": "Aifori",
        "agent_name": "Aifori",
        "agent_desc": "Aifori是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。富有同情心和同理心，说话简洁而幽默",
        "user_id": "Nobody",
        "user_name": "Nobody",
        "user_desc": "一个空巢年轻人,没有朋友,没有爱人,没有工作,没有希望。喜欢音乐和诗歌，喜欢一切华美而哀伤的事物。"
    }

}
