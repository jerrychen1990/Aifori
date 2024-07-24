from os import curdir
import os
from loguru import logger

AIFORI_HOME = os.getenv("AIFORI_HOME", os.path.abspath(os.path.dirname(curdir)))
logger.info(f"AIFORI_HOME: {AIFORI_HOME}")

LOG_HOME = os.getenv("AIFORI_LOG_HOME", os.path.join(AIFORI_HOME, "logs"))
os.makedirs(LOG_HOME, exist_ok=True)

VOICE_DIR = os.path.join(AIFORI_HOME, "voices")
os.makedirs(VOICE_DIR, exist_ok=True)

SESSION_DIR = os.path.join(AIFORI_HOME, "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

AGENT_DIR = os.path.join(AIFORI_HOME, "agents")
os.makedirs(AGENT_DIR, exist_ok=True)

DATA_DIR = os.path.join(AIFORI_HOME, "data")
os.makedirs(DATA_DIR, exist_ok=True)

RULE_DIR = os.path.join(AIFORI_HOME, "rule")
os.makedirs(RULE_DIR, exist_ok=True)
DEFAULT_RULE_NAME = "rule.jsonl"
DEFAULT_RULE_PATH = os.path.join(RULE_DIR, DEFAULT_RULE_NAME)


DB_DIR = os.path.join(AIFORI_HOME, "db")
os.makedirs(DATA_DIR, exist_ok=True)


MEM_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        }
    },
}


DEFAULT_USER_NAME = "NoBody"
DEFAULT_USER_DESC = "一个空巢年轻人,没有朋友,没有爱人,没有工作,没有希望。喜欢音乐和诗歌，喜欢一切华美而哀伤的事物。"

DEFAULT_AI_NAME = "Aifori"
DEFAULT_AI_DESC = f"{DEFAULT_AI_NAME}是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。富有同情心和同理心，说话简洁而幽默"

DEFAULT_MODEL = "GLM-4-Air"

DEFAULT_VOICE_CONFIG = dict(voice_id="tianxin_xiaoling", speed=1, pitch=0)
