from fastapi import Body, FastAPI
from aifori.agent import AIAgent
from aifori.core import UserMessage
from pydantic import BaseModel, Field
from typing import Any

from aifori.api import get_assistant
from aifori.memory import RawMemory
from loguru import logger

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
                     stream: bool = Body(default=False)) -> Response:
    assistant = get_assistant(agent_id)
    resp = assistant.chat(message=UserMessage(content=message, name=user_id), stream=stream)
    logger.debug(f"{resp=}")

    return Response(data=resp)
