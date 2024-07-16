from fastapi import Body, FastAPI
from fastapi.responses import StreamingResponse
from aifori.agent import AIAgent
from aifori.tts import tts as tts_api
from aifori.core import UserMessage
from pydantic import BaseModel, Field
from typing import Any

from aifori.api import get_assistant
from aifori.memory import RawMemory

app = FastAPI()


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


@app.get("/health")
async def health():
    return Response(data=dict(status="ok"))


@app.post("/agent/create", tags=["agent"])
async def create_agent(name: str = Body(default="Emohaa"),
                       desc: str = Body(default="Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话"),
                       model: str = Body(default="GLM-4-Flash")) -> Response:
    memory = RawMemory()
    assistant = AIAgent(name=name, desc=desc, model=model, memory=memory)
    assistant.save()
    return Response(data=assistant.get_config())


@app.post("/agent/chat", tags=["agent"])
async def chat_agent(agent_id: str = Body(...),
                     user_id: str = Body(...),
                     message: str = Body(...),
                     stream: bool = Body(default=False),
                     do_remember: bool = Body(default=True)) -> Response:
    assistant = get_assistant(agent_id)
    user_message = UserMessage(content=message, name=user_id)
    assistant_message = assistant.chat(message=user_message,  stream=stream)
    if do_remember:
        assistant.remember(user_message)
        assistant.remember(assistant_message)
    if stream:
        pass
    else:
        return Response(data=assistant_message)


@app.post("/agent/speak", tags=["agent"])
async def speak_agent(agent_id: str = Body(...),
                      message: str = Body(...),
                      stream: bool = Body(default=False),
                      tts_config: dict = Body(default=dict())) -> Response:
    assistant = get_assistant(agent_id)

    pass


@app.post("/model/tts", tags=["model"])
async def tts(message: str = Body(default="你好,我是aifori"),
              tts_config: dict = Body(default=dict())) -> StreamingResponse:
    resp = tts_api(text=message, stream=True, **tts_config)
    return StreamingResponse(resp, media_type="audio/wav")
