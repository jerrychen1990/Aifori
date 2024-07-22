from functools import wraps
import json
from fastapi import Body, FastAPI
from fastapi.responses import StreamingResponse
from aifori.agent import AIAgent
from aifori.session import SESSION_MANAGER
from aifori.tts import tts as tts_api
from aifori.core import AssistantMessage, UserMessage
from pydantic import BaseModel, Field
from typing import Any

from aifori.api import delete_assistant, get_assistant
from loguru import logger
from snippets import set_logger


app = FastAPI()
set_logger(env="dev", module_name=__name__)


class Response(BaseModel):
    code: int = Field(description="返回码,200为正常返回", default=200)
    msg: str = Field(description="返回消息", default="success")
    data: Any = Field(description="返回数据", default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }


def exception2resp(e: Exception) -> Response:
    resp = Response(code=500, msg="server internal error", data=str(e))
    return resp


def try_wrapper(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            return exception2resp(e)
    return wrapped


@app.get("/health", tags=["common"], description="检查服务是否正常")
async def health() -> Response:
    return Response(data=dict(status="ok"))


@app.post("/agent/create", tags=["agent"], description="创建一个Agent")
# @try_wrapper
async def create_agent(
        id: str = Body(default=None, description="Agent的ID,唯一键，如果不传则自动生成", examples=["test_agent"]),
        name: str = Body(default="Aifori", description="Agent的名字", example="Aifori"),
        desc: str = Body(default="Aifori是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话", description="Agent的描述"),
        model: str = Body(default="GLM-4-Flash", description="Agent使用的模型", example="GLM-4-Flash"),) -> Response:
    # memory = RawMemory()
    if id:
        assistant = get_assistant(id)
        if assistant:
            raise Exception(f"agent:{id} already exists")
    # logger.debug(f"{id=}")

    assistant = AIAgent(name=name, desc=desc, model=model, id=id)
    assistant.save()
    return Response(data=assistant.get_config())


@app.post("/agent/get", tags=["agent"], description="获取一个Agent")
# @try_wrapper
async def get_agent(id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"], embed=True)) -> Response:
    assistant = get_assistant(id)
    if not assistant:
        raise Exception(f"agent:{id} not found")
    return Response(data=assistant.get_config())


@app.post("/agent/delete", tags=["agent"], description="删除一个Agent")
# @try_wrapper
async def delete_agent(id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"], embed=True)) -> Response:
    delete_assistant(id)
    return Response(data=dict(status="ok"))


@app.post("/agent/chat", tags=["agent"], description="和Agent进行对话, 批式")
# @try_wrapper
async def chat_agent(agent_id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                     user_id: str = Body(description="用户的ID,唯一键", examples=["test_user"]),
                     session_id: str = Body(default=None, description="对话的ID,唯一键"),
                     message: str = Body(description="用户发送的消息", examples=["你好呀，你叫什么名字？"]),
                     do_remember: bool = Body(default=True, description="Agent是否记忆这轮对话")) -> Response:
    assistant = get_assistant(agent_id)
    if not assistant:
        raise Exception(f"agent:{agent_id} not found")
    user_message = UserMessage(content=message, user_id=user_id)
    assistant_message = assistant.chat(message=user_message,  stream=False, temperature=0)

    SESSION_MANAGER.add_message(user_message, to_id=agent_id, to_role="assistant", session_id=session_id)
    SESSION_MANAGER.add_message(assistant_message, to_id=user_id, to_role="user", session_id=session_id)

    return Response(data=assistant_message)


@app.post("/agent/chat_stream", tags=["agent"], description="和Agent进行对话, 流式")
# @try_wrapper
async def chat_agent_stream(agent_id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                            user_id: str = Body(description="用户的ID,唯一键", examples=["test_user"]),
                            session_id: str = Body(default=None, description="对话的ID,唯一键"),
                            message: str = Body(description="用户发送的消息", examples=["你好呀，你叫什么名字？"]),
                            do_remember: bool = Body(default=True, description="Agent是否记忆这轮对话")) -> StreamingResponse:
    logger.debug("agent chat stream")

    assistant = get_assistant(agent_id)
    user_message = UserMessage(content=message, user_id=user_id)
    assistant_message = assistant.chat(message=user_message,  stream=True)

    SESSION_MANAGER.add_message(user_message, to_id=agent_id, to_role="assistant", session_id=session_id)

    # assistant_message = assistant.remember(assistant_message)

    def gen():
        message = ""
        yield json.dumps(dict(assistant_id=agent_id)) + "\n"
        for item in assistant_message.content:
            # logger.info(f"{item=}")
            yield json.dumps(dict(chunk=item), ensure_ascii=False) + "\n"
            message += item
        message = AssistantMessage(content=message, user_id=agent_id)
        logger.debug(f"remembering assistant message: {message}")
        SESSION_MANAGER.add_message(message, to_id=user_id, to_role="user", session_id=session_id)

        # yield json.dumps(dict(assistant_id=agent_id, message=message), ensure_ascii=False) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


@app.post("/agent/speak_stream", tags=["agent"], description="让Agent朗读文字, 流式返回")
# @try_wrapper
async def speak_agent_stream(agent_id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                             message: str = Body(description="需要说出来的文字内容", examples=["你好呀，我的名字叫Aifori"]),
                             tts_config: dict = Body(default=dict(), description="tts的配置")) -> StreamingResponse:
    logger.debug(f"agent speak stream with {agent_id=}")
    assistant = get_assistant(agent_id)
    if not assistant:
        raise Exception(f"agent:{agent_id} not found")
    voice = assistant.speak(message=message, stream=True, **tts_config)
    logger.debug(f"{voice=}")
    return StreamingResponse(voice.content, media_type="audio/mp3")


@app.post("/model/tts", tags=["model"], description="测试tts(text2speech)模型")
# @try_wrapper
async def tts(message: str = Body(default="你好呀，我的名字叫Aifori", description="需要说出来的文字内容"),
              tts_config: dict = Body(default=dict(), description="tts模型的配置")) -> StreamingResponse:
    resp = tts_api(text=message, stream=True, **tts_config)
    return StreamingResponse(resp, media_type="audio/wav")


@app.post("/session/clear", tags=["session"], description="清空session的历史")
async def clear_session(session_id: str = Body(description="session_id", examples=["test_session"], embed=True)) -> Response:
    SESSION_MANAGER.clear_session(session_id)
    return Response(data=dict(status="ok"))
