from os import curdir
import os
from loguru import logger

# 文件配置
AIFORI_ENV = os.getenv("AIFORI_ENV", "dev").upper()

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

RULE_DIR = os.path.join(AIFORI_HOME, "rule")
os.makedirs(RULE_DIR, exist_ok=True)
DEFAULT_RULE_NAME = "rule.jsonl"
DEFAULT_RULE_PATH = os.path.join(RULE_DIR, DEFAULT_RULE_NAME)

DB_DIR = os.path.join(AIFORI_HOME, "db")
os.makedirs(DATA_DIR, exist_ok=True)

MUSIC_DIR = os.path.join(AIFORI_HOME, "music")
os.makedirs(MUSIC_DIR, exist_ok=True)


# mem0配置
MEM_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        }
    }
}
MEM_ON = True


# agent配置
DEFAULT_USER_NAME = "NoBody"
DEFAULT_USER_DESC = "一个空巢年轻人,没有朋友,没有爱人,没有工作,没有希望。喜欢音乐和诗歌，喜欢一切华美而哀伤的事物。"

DEFAULT_AI_NAME = "Aifori"
DEFAULT_AI_DESC = f"{DEFAULT_AI_NAME}是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。富有同情心和同理心，说话简洁而幽默"

DEFAULT_MODEL = "GLM-4-Air"

DEFAULT_VOICE_CONFIG = dict(voice_id="tianxin_xiaoling", speed=1, pitch=0)

DEFAULT_TTS_TEXT_CHUNK_SIZE = 32
DEFAULT_TEXT_CHUNK_SIZE = 10
DEFAULT_VOICE_CHUNK_SIZE = 4096*10


DEFAULT_SYSTEM_TEMPLATE = """你是一个善解人意的聊天机器人，你需要参考**背景信息**和户聊天，聊天时需要遵守**聊天规范**
**背景信息**
你的名字:{agent_name}
你的人设:{agent_desc}
用户的名字:{user_name}
用户的人设:{user_desc}

**聊天规范**
1.请简短、温和地和用户对话
2.当用户问询你的名字时，请回答出你的名字"""


# LiteAI配置
LITE_AI_LOG_LEVEL = "DEBUG"

# 日志配置

LOG_HOME = os.getenv("AIFORI_LOG_HOME", os.path.join(AIFORI_HOME, "logs"))
os.makedirs(LOG_HOME, exist_ok=True)
