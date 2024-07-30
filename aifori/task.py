# tasks.py
import datetime
from celery import Celery
from loguru import logger
from aifori.memory import MEM

# 创建 Celery 应用，指定 Redis 作为消息代理
app = Celery('task', broker='redis://localhost:6379/0')


@app.task
def add_message2memory(message: dict):
    logger.debug(f"executing task add message2memory with {message}")
    user_id, agent_id = (message["from_id"], message["to_id"]) if message["from_role"] == "user" else (message["to_id"], message["from_id"])
    logger.debug(f"add data={message['content']} {user_id=} {agent_id=} to mem")

    MEM.add(data=message["content"], user_id=user_id, agent_id=agent_id)
    logger.debug("done")


if __name__ == "__main__":
    message = {'id': 186, 'session_id': '7ed9b796-1322-461a-bb5b-68deeee75184', 'from_role': 'assistant', 'from_id': 'fe918725-ee28-4add-834b-46cb1ecaf56b',
               'content': '作为AI，我没有个人喜好，但我可以欣赏很多歌手的才华。如果你愿意分享，我很乐意听听你喜欢的歌手，也许我们可以一起探讨他们的音乐和诗歌。你最近有没有听什么让你印象深刻的歌曲？', 'to_role': 'user', 'to_id': '34d0f275-1e7c-4899-921c-94b6338856c1', 'create_datetime': datetime.datetime(2024, 7, 30, 17, 35, 36, 408470)}
    add_message2memory(message)
