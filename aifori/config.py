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
