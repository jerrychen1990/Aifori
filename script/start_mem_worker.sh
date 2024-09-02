#!/bin/bash

# 检查 Redis 是否在运行
if pgrep redis-server > /dev/null
then
    echo "Redis is already running."
else
    echo "Redis is not running. Starting Redis..."
    redis-server &
fi
# 开启消息处理队列
echo "Starting Celery worker to handle messages..."
celery -A aifori.task worker --loglevel=info