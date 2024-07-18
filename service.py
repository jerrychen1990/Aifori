import json
from fastapi import Body, FastAPI
from fastapi.responses import StreamingResponse
from aifori.agent import AIAgent
from aifori.tts import tts as tts_api
from aifori.core import UserMessage
from pydantic import BaseModel, Field
from typing import Any

from aifori.api import get_assistant
from aifori.memory import RawMemory
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


@app.get("/health", tags=["common"], description="检查服务是否正常")
async def health() -> Response:
    return Response(data=dict(status="ok"))


@app.post("/agent/create", tags=["agent"], description="创建一个Agent")
async def create_agent(
        id: str = Body(default=None, description="Agent的ID,唯一键，如果不传则自动生成", examples=["test_agent"]),
        name: str = Body(default="Aifori", description="Agent的名字", example="Aifori"),
        desc: str = Body(default="Aifori是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话", description="Agent的描述"),
        model: str = Body(default="GLM-4-Flash", description="Agent使用的模型", example="GLM-4-Flash"),) -> Response:
    memory = RawMemory()
    assistant = AIAgent(name=name, desc=desc, model=model, memory=memory, id=id)
    assistant.save()
    return Response(data=assistant.get_config())


@app.post("/agent/get", tags=["agent"], description="获取一个Agent")
async def create_agent(id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"], embed=True)) -> Response:
    assistant = get_assistant(id)
    return Response(data=assistant.get_config())


@app.post("/agent/chat", tags=["agent"], description="和Agent进行对话, 批式")
async def chat_agent(id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                     user_id: str = Body(description="用户的ID,唯一键", examples=["test_user"]),
                     message: str = Body(description="用户发送的消息", examples=["你好呀，你叫什么名字？"]),
                     do_remember: bool = Body(default=True, description="Agent是否记忆这轮对话")) -> Response:
    logger.info("agent chat")
    assistant = get_assistant(id)
    user_message = UserMessage(content=message, id=user_id)
    assistant_message = assistant.chat(message=user_message,  stream=False)
    if do_remember:
        assistant.remember(user_message)
        assistant_message = assistant.remember(assistant_message)
    return Response(data=assistant_message)


@app.post("/agent/chat_stream", tags=["agent"], description="和Agent进行对话, 流式")
async def chat_agent_stream(id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                            user_id: str = Body(description="用户的ID,唯一键", examples=["test_user"]),
                            message: str = Body(description="用户发送的消息", examples=["你好呀，你叫什么名字？"]),
                            do_remember: bool = Body(default=True, description="Agent是否记忆这轮对话")) -> StreamingResponse:
    logger.debug("agent chat stream")

    assistant = get_assistant(id)
    user_message = UserMessage(content=message, id=user_id)
    assistant_message = assistant.chat(message=user_message,  stream=True)
    if do_remember:
        assistant.remember(user_message)
        assistant_message = assistant.remember(assistant_message)

    def gen():
        yield json.dumps(dict(assistant_id=id)) + "\n"
        for item in assistant_message.content:
            logger.info(f"{item=}")
            yield json.dumps(dict(chunk=item), ensure_ascii=False) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


@app.post("/agent/speak_stream", tags=["agent"], description="让Agent朗读文字, 流式返回")
async def speak_agent_stream(id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                             message: str = Body(description="需要说出来的文字内容", examples=["你好呀，我的名字叫Aifori"]),
                             tts_config: dict = Body(default=dict(), description="tts的配置")) -> StreamingResponse:
    assistant = get_assistant(id)
    voice = assistant.speak(message=message, stream=True, **tts_config)
    return StreamingResponse(voice.content, media_type="audio/mp3")


@app.post("/model/tts", tags=["model"], description="测试tts(text2speech)模型")
async def tts(message: str = Body(default="你好呀，我的名字叫Aifori", description="需要说出来的文字内容"),
              tts_config: dict = Body(default=dict(), description="tts模型的配置")) -> StreamingResponse:
    resp = tts_api(text=message, stream=True, **tts_config)
    return StreamingResponse(resp, media_type="audio/wav")
