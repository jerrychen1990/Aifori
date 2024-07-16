from os import curdir
import os
from loguru import logger

AIFORI_HOME = os.getenv("AIFORI_HOME", os.path.abspath(os.path.dirname(curdir)))
logger.info(f"AIFORI_HOME: {AIFORI_HOME}")

VOICE_DIR = os.path.join(AIFORI_HOME, "voices")
os.makedirs(VOICE_DIR, exist_ok=True)

SESSION_DIR = os.path.join(AIFORI_HOME, "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

AGENT_DIR = os.path.join(AIFORI_HOME, "agents")
os.makedirs(AGENT_DIR, exist_ok=True)

DATA_DIR = os.path.join(AIFORI_HOME, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_DIR = os.path.join(AIFORI_HOME, "db")
os.makedirs(DATA_DIR, exist_ok=True)

LLM_MODELS = ["emohaa", "charglm-3", "glm-4-airx"]

DEFAULT_USER_NAME = "NoBody"
DEFAULT_USER_DESC = "一个空巢年轻人,没有朋友,没有爱人,没有工作,没有希望。喜欢音乐和诗歌，喜欢一切华美而哀伤的事物。"

DEFAULT_AI_NAME = "Samantha"
DEFAULT_AI_DESC = f"{DEFAULT_AI_NAME}是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。富有同情心和同理心，说话简洁而幽默"


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
